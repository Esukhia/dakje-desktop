# Release note
## Version 1.0 (2019.1.6)

### Main Features
- New UI
- Tokens' attributes editing (depends on cql rules)
- Splitting/Merging tokens
- Auto updating trie/dict when adding new words
- Saving data using databases(sqlite3), not files.
- Others
    - Choosing levels/pos to highlight
    - If token's pos is "OOV", it will popup a window to edit DICT

### Known Issues
- Haven't tested for big text
- Haven't implemented replace function
- Haven't implemented loading previous rules for a token
- Dictionary dialog's deleting function will cause a bug when filtering is on.
