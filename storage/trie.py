import os

from pybo import BasicTrie, PyBoTrie, Config
from pybo import BoSyl

from Configure import BASE_DIR

bt = PyBoTrie(BoSyl(), 'POS',
              config=Config(os.path.join(BASE_DIR, "config.yaml")))
bt.add("word", data='NOUNᛃᛃᛃ')
bt.add("word", data='VERBᛃᛃᛃ')
bt.deactivate_word('word')
print(bt.has_word("word"))
