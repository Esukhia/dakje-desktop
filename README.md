# tibetaneditor

This PyQt5 project is a beta version of readability editor for the Tibetan language.

The readability editor assesses the readability of a text by highlighting words according to their level of difficulty. Levels of frequency are defined by analysing the frequency of words in a given language.

The beta version allows users to:

1. write or paste text in the editor
2. segment and highlight the text by clicking on the segment icon

To test the tool, paste the text from test_source.txt in the editor and click the segmentation icon. The result should look like this:

![test](test_result.png)

Features comming soon:
- spell-checking
- rules and vocab list editing for segmentation/POS tagging/spell-checking
- suggestion of spelling correction
- suggestion of vocabulary alternative

## Release note

- Version: 0.8 (2017/1/2)
    
    * Merge the fork https://github.com/Esukhia/TibEdit/tree/add-support-for-affixed-POS ,the main change is to use the Tokenization (formerly segmentation) and ProcessingPipeline to handle with segmentation and words tagging.
    * Details:
        - RDRPOSTagger4Local.py works even with current install of RDR (modified paths)
        - create an entry point to RDR that does not care about paths (it is the copy of what I had for my clean install of RDR)
        - adds mechanism to choose what language and what model to use
        - ensures to only initialize the tagger when WordManager is instanciated or when we change model
        - adds mechanism to add tags directly to words (list of Word objects), but also includes a classic mode (the one used now)
        - filters which Word obj should be tagged and keeps an index to reinsert tags in the corresponding obj
        - implements better RDR models for Tibetan
        - improves pytib results by removing unnecessary lexical resources
        - solves bug of disapearing punctuation (obj.content = \n + punctation)
        - solves once and for all the problem of / in the original string by internally using a rune unicode character as separator. (the users still see /)
        - prepares pytib for coming new post-tagging processing of words
        - segmentation and re-segmentation works
        - include two files (try_pytib.py, try-new-RDR-api.py) to test the new features
        - added spaces around non-tib punctuation is solved
        - revert _ to spaces before displaying in the editor.

- Version: 0.71 (2017/12/13)

    * Fix the error occurs when adding new sentences at the end of the article after segmenting
    * Fix the error occurs when segmenting a new blank line

- Version: 0.7 (2017.11.29)

    *  Changed the processing logic from "based on words" to "based on blocks"  which speeds up the performance.

- Version: 0.6 (2017.10.26)
	
	* Add a new feature "Customed words level list and rules"
	* Add a new feature "Profiles managements"
	* Refactor codes to be more object-oriented
	* Make some adjustments in UI
	
- Version: 0.5 (2017.10.14)
	
	* Fix "change-tag dropdown appears in the wrong position after resizing the window"
	* Fix "find & replace triggers change-tag dropdown wrongly"
	* Fix "editor somtimes doesn't save the change in real-time editing"

- Version: 0.4 (2017.10.02)

    * Add Find & Replace function
    * Add real-time detecting when editing
	* Change the tag dropdown to fixed mode
	* Fix the highlight bug which leads to bad performance

- Version: 0.3
    
    * Tagging by clicking on the part of speech
    * Fix the highlight problems in tagging and re-segment
    * Add warning when switching modes from plain text to other

- Version: 0.2
	
	* POS Tagging
	* Level List Color Selection
	* Words Counting
	* Highlighter Optimized
	* Optional Display by Spaces or Tags
