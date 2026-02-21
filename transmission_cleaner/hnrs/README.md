## Adding HNR rule functions:
1. Copy the template from `transmission_cleaner/hnrs/_template.py` into a new file in the same directory
    - Change the name of the file to the name or shorthand of the website
    - Adapt the docstring where necassry
    - Add the actual rules from the site into the docstring
2. Implement the function to check the torrent against the HNR.
    -Return True = the torrent is not a HNR, False = the torrent is violating the HNR rules (should not be deleted)
3. Add the import to `transmission_cleaner/hnrs/__init__.py`
4. Add an entry into the `hnr_map` dictionary under `transmission_cleaner/hnrs/check.py`
    - If multiple trackers are possible, add an entry for each tracker
5. (Optional) If it's more complex, please add a test
