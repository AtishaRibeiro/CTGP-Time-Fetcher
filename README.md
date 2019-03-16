# CTGP-Time-Fetcher
Fetches times from the CTGP-R ghost database

### About

Originally meant to automatically update the BNL tops, but can be easily used for other countries.
Tops are read from and written to a json file (see `BNL.json` for an example.)
Times are all obtained from http://www.chadsoft.co.uk/time-trials/


### Using `GhostFetcher.py`

`GhostFetcher.py` can be used seperately as well to get all ghosts from specified countries starting from a given date.
The country codes can be found at the beginning of the file, in `COUNTRY_FLAGS`.
A text file is produced containing all the found times, including a link to the ghost.

Example:
```python
countries_to_check = [67, 88, 94]
date_str = "2019-03-13"
```

This code checks for ghosts set in countries [Belgium, Luxembourg, Netherlands].
It also only searches for ghosts that are set after 2019-03-13

Keep in mind that a player can be from one country, but set a time for another. This is **not** accounted for.
