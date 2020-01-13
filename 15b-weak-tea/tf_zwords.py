#!/usr/bin/env python
import sys, tf_config, tf_15b

def filter_words(words, substring):
    return [word for word in words if substring in word]

config = tf_config.LoadConfig('tf_zwords.json')
if (__name__ == "__main__"):
    tf_config.ExecuteConfig(config, sys.argv[1])
