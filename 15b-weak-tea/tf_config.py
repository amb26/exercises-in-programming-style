#!/usr/bin/env python
import sys, json
# Implements the "weak tea" configuration language/integration language, orchestrating a collection of free,
# module-global functions into an openly authorable workflow

# Introspect on the set of loaded modules, resolving an expression x.y into the global named y of module x
# If the expression includes no period, resolve onto the builtin with that name
def FetchModuleGlobal(name):
    parts = name.split('.')
    if len(parts) == 1:
       moduleName = '__builtin__'
       name = parts[0]
    else:
       moduleName, name = parts
    # Hack: Assume that any module we can't find must have been intended to be a reference to the main module
    module = sys.modules[moduleName] if moduleName in sys.modules else sys.modules['__main__']
    return getattr(module, name)

# Load a configuration language file, if necessary merging its contents with that of any parent
def LoadConfig(path_to_file):
    with open(path_to_file) as configText:
        config = json.load(configText)
    if ('parent' in config):
        parentConfig = FetchModuleGlobal(config['parent'])
        # This line implements the "program addition operator"
        config['steps'].update(parentConfig['steps'].copy())
    return config

# Insert the record rec with key key into the array of steps at the position determined by its priority
# If its referent is not yet in the array, do nothing and return false
def HonourConstraint(steps, rec, key):
    priority = rec['priority']
    if priority == "first":
        newIndex = 0
    elif priority == "last":
        newIndex = 1
    else:
        priorityParts = priority.split(":")
        offset = 0 if priorityParts[0] == "before" else 1
        try:
            targetIndex = next(index for index, step in enumerate(steps) if step['namespace'] == priorityParts[1])
            newIndex = targetIndex + offset
        except StopIteration:
            return False
    newStep = {'namespace': key, 'func': FetchModuleGlobal(rec['func']), 'args': rec.get('args', [])}
    steps.insert(newIndex, newStep)
    return True

# Sort the hash representation of steps in a configuration into the priority-sorted array structure, ready for execution
def ConfigToSteps(configSteps):
    steps = [];
    while len(configSteps) > 0:
        for key in configSteps.keys():
            rec = configSteps[key]
            applied = HonourConstraint(steps, rec, key)
            if applied:
                del configSteps[key]
    return steps

# Execute the given config, with the given initial argument directArg
def ExecuteConfig(config, directArg):
   argMap = {'directArg': directArg }
   steps = ConfigToSteps(config['steps'])
   for step in steps:
       args = map(lambda arg: argMap[arg[1:]] if isinstance(arg, basestring) and arg[0] == '$' else arg, step['args'])
       argMap[step['namespace']] = step['func'](*args)
