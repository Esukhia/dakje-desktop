##Test1

The string "བཀྲ་ཤིས་བདེ་ལེགས་ཕུན་སུམ་ཚོགས།" is first segmented and tagged as "བཀྲ་ཤིས་/NOUNབདེ་ལེགས་/NOUNཕུན་སུམ་ཚོགས/OOV།/PUNCT". Highlighting has the following issues:

* We can't highlight the two first words with the string "བཀྲ་ཤིས་བདེ་ལེགས" regardless of the view.
* We can't highlight the 2nd syllable of the 1st word and the 1st syllable of the second word with the string "ཤིས་བདེ་"
* We can't highlight words tagged "OOV" in simple text view
