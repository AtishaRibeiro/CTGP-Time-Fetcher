# TT Bot
Bot that interacts with the CTGP-R Database in various ways.
Currently configured to track the BNL tops.

### Usage

For using the bot only the `TT Bot` directory is needed, you can throw the rest away.
Before running a `Config.py`file must be added in de directory which looks as follows:

```python
TOKEN = "Discord Bot Token"
CHANNEL = ID of channel where commands are read
UPDATE_CHANNEL = ID of channel where the updates are posted
MODERATOR = ID of moderator role
DMCHANNEL = ID of the bot's dm channel
```
Fill in the correct token and id's.

You can then run the bot by executing the `run.sh` script.
`Python3`, `pip3` and `virtualenv` must be installed in order to run this properly.
If there is no database present add argument `-db`.

Example:
```
> chmod +x ./run.sh
> ./run.sh -db
```
