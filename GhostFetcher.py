import json
import urllib.request
import codecs
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
            exit()

        self.ms_total = self.miliseconds + (self.seconds * 1000) + (self.minutes * 60000)

    def __str__(self):
        return self.string

class Ghost:
    """Class used to represent a ghost"""

    def __init__(self, dict):
        self.country = dict["Country"]
        self.name = dict["Name"]
        self.time = FinishTime(dict["Time"])
        self.ghost = dict["Ghost"]

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

    def __str__(self):
        return "{} {}: {} ({})".format(self.country, self.name, str(self.time), self.ghost)

    def to_dict(self):
        return {
            "Country": self.country,
            "Name":  self.name,
            "Time": str(self.time),
            "Ghost": self.ghost
        }

class DataFetcher:
    """Class used to fetch data from the undocumented API at http://tt.chadsoft.co.uk"""

    def __init__(self):
        self.base_url = "http://tt.chadsoft.co.uk"
        self.leaderboards = "/original-track-leaderboards.json"
        self.ghost_url = "http://www.chadsoft.co.uk/time-trials"

    def get_ghosts(self, countries, cmp_date):
        """Looks for times that were set by players from 'countries' starting from cmp_date"""

        new_ghosts = dict()

        # get info on all tracks
        data = None
        with urllib.request.urlopen(self.base_url + self.leaderboards) as url:
            data = json.loads(url.read().decode("utf-8-sig"))

        # loop over every track
        for track in data["leaderboards"]:

            # construct track name based on category
            track_name = track["name"]
            try:
                category = track["categoryId"]
                track_name = track_name + (category == 1)*" (Glitch)" + (category == 16)*" (Alternate)"
            except KeyError:
                pass

            print(track_name)
            new_ghosts[track_name] = list()
            track_link = track["_links"]["item"]["href"]

            # get data from current track
            track_ghosts = None
            with urllib.request.urlopen(self.base_url + track_link) as track_url:
                track_ghosts = json.loads(track_url.read().decode("utf-8-sig"))

            # loop over all ghosts to find the ones that match the given criteria
            for ghost in track_ghosts["ghosts"]:
                try:
                    if ghost["playersFastest"] == True:
                        if ghost["country"] in countries:
                            ghost_time = datetime.strptime(ghost["dateSet"], "%Y-%m-%dT%H:%M:%SZ")
                            if ghost_time >= cmp_date:
                                ghost_Ghost = Ghost({
                                    "Country": COUNTRY_FLAGS[ghost["country"]],
                                    "Name": ghost["player"],
                                    "Time": ghost["finishTimeSimple"],
                                    "Ghost": self.ghost_url + ghost["href"][:-3] + "html"})

                                new_ghosts[track_name].append(ghost_Ghost)

                except KeyError:
                    # some players don't have a country set so these will throw a KeyError for ghost["Country"]
                    continue

        return new_ghosts

if __name__ == "__main__":
    # country numbers from COUNTRY_FLAGS
    countries_to_check = [67]
    date_str = "2019-03-01"
    date = datetime.strptime(date_str, "%Y-%m-%d")
    df = DataFetcher()
    new_ghosts = df.get_ghosts(countries_to_check, date)

    with open("ghosts(" + date_str + ").txt", 'w') as file:
        for track in new_ghosts:
            file.write(track + ":\n")

            for ghost in new_ghosts[track]:
                file.write('\t' + str(ghost) + '\n')