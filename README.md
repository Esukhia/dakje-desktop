# Release note

## Version 1.1 (2019.1.26)
- Using django orm to handle database manipulation, django admin site was also added.(name: admin, pwd: admin)
- Find/Replace function using plain text or cql queries.
- Installer for Windows users.

## Version 1.0 (2019.1.6)
- New UI
- Tokens' attributes editing (depends on cql rules)
- Splitting/Merging tokens
- Auto updating trie/dict when adding new words
- Saving data using databases(sqlite3), not files.
- Others
    - Choosing levels/pos to highlight
    - If token's pos is "OOV", it will popup a window to edit DICT

## Known Issues
- Haven't tested for big text
- Dictionary dialog's deleting function will cause a bug when filtering is on.
