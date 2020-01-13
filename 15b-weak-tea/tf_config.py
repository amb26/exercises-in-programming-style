#!/usr/bin/env python
import sys, json

def FetchModuleGlobal(name):
    parts = name.split('.')
    if len(parts) == 1:
       moduleName = '__builtin__'
       name = parts[0]
    else:
       moduleName, name = parts
    module = sys.modules[moduleName] if moduleName in sys.modules else sys.modules['__main__']
    return getattr(module, name)

def LoadConfig(path_to_file):
    with open(path_to_file) as configText:
        config = json.load(configText)
    if ('parent' in config):
        parentConfig = FetchModuleGlobal(config['parent'])
        print parentConfig
        # This line implements the "program addition operator"
        config['steps'].update(parentConfig['steps'].copy())
    return config

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

def ConfigToSteps(configSteps):
    steps = [];
    while len(configSteps) > 0:
        for key in configSteps.keys():
            rec = configSteps[key]
            applied = HonourConstraint(steps, rec, key)
            if applied:
                del configSteps[key]
    return steps

def ExecuteConfig(config, directArg):
   argMap = {'directArg': directArg }
   steps = ConfigToSteps(config['steps'])
   for step in steps:
       args = map(lambda arg: argMap[arg[1:]] if isinstance(arg, basestring) and arg[0] == '$' else arg, step['args'])
       argMap[step['namespace']] = step['func'](*args)
