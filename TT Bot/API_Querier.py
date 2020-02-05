import json
import urllib.request
import codecs
import asyncio
import aiohttp
from datetime import datetime

# based on http://www.chadsoft.co.uk/img/flags_32.png
COUNTRY_FLAGS = {
      1: '🇯🇵', # Japan
      8: '🇦🇮', # Anguilla
      9: '🇦🇬', # Antigua and Barbuda
     10: '🇦🇷', # Argentina
     11: '🇦🇼', # Aruba
     12: '🇧🇸', # Bahamas
     13: '🇧🇧', # Barbados
     14: '🇧🇿', # Belize
     15: '🇧🇴', # Bolivia
     16: '🇧🇷', # Brazil
     17: '🇻🇬', # British Virgin Islands
     18: '🇨🇦', # Canada
     19: '🇰🇾', # Cayman Islands
     20: '🇨🇱', # Chile
     21: '🇨🇴', # Colombia
     22: '🇨🇷', # Costa Rica
     23: '🇩🇲', # Dominica
     24: '🇩🇴', # Dominican Republic
     25: '🇪🇨', # Ecuador
     26: '🇸🇻', # El Salvador
     27: '🇬🇫', # French Guiana
     28: '🇬🇩', # Grenada
     29: '🇬🇵', # Guadeloupe
     30: '🇬🇹', # Guatemala
     31: '🇬🇾', # Guyana
     32: '🇭🇹', # Haiti
     33: '🇭🇳', # Honduras
     34: '🇯🇲', # Jamaica
     35: '🇲🇶', # Martinique
     36: '🇲🇽', # Mexico
     37: '🇲🇸', # Montserrat
     38: '🏳️', # Netherlands Antilles
     39: '🇳🇮', # Nicaragua
     40: '🇵🇦', # Panama
     41: '🇵🇾', # Paraquay
     42: '🇵🇪', # Peru
     43: '🇰🇳', # Saint Kitts and Nevis
     44: '🇱🇨', # Saint Lucia
     45: '🇻🇨', # Saint Vincent and Grenadines
     46: '🇸🇷', # Suriname
     47: '🇹🇹', # Trinidad and Tobago
     48: '🇹🇨', # Turks and Caicos Islands
     49: '🇺🇸', # United States
     50: '🇺🇾', # Uruguay
     51: '🇻🇮', # U.S. Virgin Islands
     52: '🇻🇪', # Venezuela
     64: '🇦🇱', # Albania
     65: '🇦🇺', # Australia
     66: '🇦🇹', # Austria
     67: '🇧🇪', # Belgium
     68: '🇧🇦', # Bosnia and Herzegovina
     69: '🇧🇼', # Botswana
     70: '🇧🇬', # Bulgaria
     71: '🇭🇷', # Croatia
     72: '🇨🇾', # Cyprus
     73: '🇨🇿', # Czechia
     74: '🇩🇰', # Denmark
     75: '🇪🇪', # Estonia
     76: '🇫🇮', # Finland
     77: '🇫🇷', # France
     78: '🇩🇪', # Germany
     79: '🇬🇷', # Greece
     80: '🇭🇺', # Hungary
     81: '🇮🇸', # Iceland
     82: '🇮🇪', # Ireland
     83: '🇮🇹', # Italy
     84: '🇱🇻', # Latvia
     85: '🇱🇸', # Lesotho
     86: '🇱🇮', # Liechtenstein
     87: '🇱🇹', # Lithuania
     88: '🇱🇺', # Luxembourg
     89: '🇲🇰', # North Macedonia
     90: '🇲🇹', # Malta
     91: '🇷🇸', # Serbia (?)
     92: '🇲🇿', # Mozambique
     93: '🇳🇦', # Namibia
     94: '🇳🇱', # Netherlands
     95: '🇳🇿', # New Zealand
     96: '🇳🇴', # Norway
     97: '🇵🇱', # Poland
     98: '🇵🇹', # Portugal
     99: '🇷🇴', # Romania
    100: '🇷🇺', # Russia
    101: '🇷🇸', # Serbia (?)
    102: '🇸🇰', # Slovakia
    103: '🇸🇮', # Slovenia
    104: '🇿🇦', # South Africa
    105: '🇪🇸', # Spain
    106: '🇸🇿', # Swaziland
    107: '🇸🇪', # Sweden
    108: '🇨🇭', # Switzerland
    109: '🇹🇷', # Turkey
    110: '🇬🇧', # United Kingdom
    111: '🇿🇲', # Zambia
    112: '🇿🇼', # Zimbabwe
    113: '🇦🇿', # Azerbaijan
    114: '🇲🇷', # Mauritania
    115: '🇲🇱', # Mali
    116: '🇳🇪', # Niger
    117: '🇹🇩', # Chad
    118: '🇸🇩', # Sudan
    119: '🇪🇷', # Eritrea
    120: '🇩🇯', # Djibouti
    121: '🇸🇴', # Somalia
    128: '🇿🇼', # Zimbabwe
    144: '🇰🇷', # South Korea
    145: '🇭🇰', # Hong Kong
    148: '🇹🇼', # Taiwan
    152: '🇮🇩', # Indonesia
    153: '🇸🇬', # Signapore
    154: '🇹🇭', # Thailand
    155: '🇵🇭', # Philippines
    156: '🇲🇾', # Malaysia
    160: '🇨🇳', # China
    168: '🇦🇪', # United Arab Emirates
    169: '🇮🇳', # India
    170: '🇬🇶', # Equatorial Guinea
    171: '🇴🇲', # Oman
    172: '🇶🇦', # Qatar
    173: '🇰🇼', # Kuwait
    174: '🇸🇦', # Saudi Arabia
    175: '🇸🇾', # Syria
    176: '🇧🇭', # Bahrain
    177: '🇯🇴', # Jordan
}

class FinishTime:
    """Class used to represent finish time of ghosts"""

    def __init__(self, t_string):
        try:
            self.minutes = int(t_string[0:2])
            self.seconds = int(t_string[3:5])
            self.miliseconds = int(t_string[6:9])
            self.string = t_string
        except ValueError:
            print("Incorrect time format used: " + t_string)

        self.ms_total = self.miliseconds + (self.seconds * 1000) + (self.minutes * 60000)

    def __str__(self):
        return self.string

class Ghost:
    """Class used to represent a ghost"""

    def __init__(self, country, name, time, ghost):
        self.country = country
        self.name = name
        self.time = FinishTime(time)
        self.ghost = ghost
        # this is only used to update tops
        self.new = False

    def __lt__(self, other):
        return self.time.ms_total < other.time.ms_total

    def __gt__(self, other):
        return self.time.ms_total > other.time.ms_total

    def __eq__(self, other):
        return self.time.ms_total == other.time.ms_total

    def __ge__(self, other):
        return self.time.ms_total >= other.time.ms_total

    def __le__(self, other):
        return self.time.ms_total <= other.time.ms_total

    def __hash__(self):
        return self.time.ms_total

    def to_str(self, markdown=False):
        if markdown:
            # check if it is a link
            if ('.' in self.ghost):
                return "{} {}: {}".format(self.country, self.name, str(self.time))
            else:
                return "{} {}: [{}]({})".format(self.country, self.name, str(self.time), self.ghost)
        return "{} {}: {} ({})".format(self.country, self.name, str(self.time), self.ghost)

class APIQuerier:
    """Class used to fetch ghosts from the API"""

    def __init__(self, countries, client, database):
        self.base_url = "http://tt.chadsoft.co.uk"
        self.leaderboards = "/original-track-leaderboards.json"
        self.players = "/players.json"
        self.ghost_url = "http://www.chadsoft.co.uk/time-trials"
        self.countries = countries
        self.client = client
        self.DB = database

    async def get_json(self, url):
        async with self.client.get(url) as response:
            if response.status != 200:
                return None
            else:
                return await response.read()

    async def get_ghosts(self):
        """Looks for times that were set by players from the database"""

        new_ghosts = dict()

        # get info on all tracks
        data_raw = await self.get_json(self.base_url + self.leaderboards)
        if data_raw is None:
            print("Failed to access database")
            return new_ghosts
        data = json.loads(data_raw.decode("utf-8-sig"))

        # loop over every track
        for track in data["leaderboards"]:

            # construct track name based on category
            track_name = track["name"]
            try:
                category = track["categoryId"]
                track_name = track_name + (category == 1)*" (Glitch)" + (category == 16)*" (Shortcut)"
            except KeyError:
                pass

            print("Reading " + track_name)
            new_ghosts[track_name] = list()
            track_link = track["_links"]["item"]["href"]

            # get data from current track
            track_ghosts_raw = await self.get_json(self.base_url + track_link)
            if track_ghosts_raw is None:
                print("Failed to read " + track_name)
                continue
            track_ghosts = json.loads(track_ghosts_raw.decode("utf-8-sig"))

            for ghost in track_ghosts["ghosts"]:
                result = await self.analyse_ghost(track_name, ghost)
                if result is not None:
                    new_ghosts[track_name].append(result)

        return new_ghosts

    async def analyse_ghost(self, track, ghost, player_id=None, country=""):
        """check if a ghost matches the criteria"""
        ghost_obj = None

        if ghost["playersFastest"] == True:
            player_id = ghost["playerId"]

            if self.DB.player_exists(player_id):
                #check if the ghost is already in our database
                if self.DB.insert_pb(player_id, track, ghost["hash"], ghost["finishTimeSimple"]):
                    country, player_name = self.DB.get_player_info(player_id)
                    ghost_obj = Ghost(country, player_name, ghost["finishTimeSimple"], self.ghost_url + ghost["href"][:-3] + "html")

        return ghost_obj

    async def get_players(self):
        """Gets all players from from 'countries'"""

        print("trying to fetch players")
        data_raw = None
        # try max 5 times
        tries = 5
        while tries > 0:
            print("{} tries left".format(tries))
            data_raw = await self.get_json(self.base_url + self.players)
            if data_raw is not None:
                tries = 0
            tries -= 1

        if data_raw is None:
            print("Failed to access database")
            return False
        data = json.loads(data_raw.decode("utf-8-sig"))

        for player in data["players"]:
            country = player["country"]
            if country in self.countries:
                country_flag = COUNTRY_FLAGS[country]
                if self.DB.set_player(player["playerId"], player["miiName"], country_flag, False):
                    print("Added player {}".format(player["miiName"]))



