import json
import csv
import asyncio
from datetime import datetime
from enum import Enum
from DB import DB
from API_Querier import Ghost, APIQuerier

class ImprovementType(Enum):
    none = 0
    improvement = 1
    new = 2
    new_1st = 3
    tie_1st = 4
    improvement_1st = 5

class Tops:
    """Class that handles the top10 of a region"""

    def __init__(self, db, client):
        self.countries = [67, 88, 94]
        self.DB = db
        self.aq = APIQuerier(self.countries, client, self.DB)

    def add_time(self, new_time, track):
        """Attempts to add 'new_time' to the top10, only adds if it belongs there"""

        if self.DB.is_banned(new_time.ghost):
            return ImprovementType.none, 4

        action = ImprovementType.new
        new_time.new = True
        top10 = [Ghost(x[0], x[1], x[2], x[3]) for x in self.DB.get_top10(track)]
        if len(top10) == 0:
            self.DB.insert_top_entry(track, new_time.name, str(new_time.time), new_time.ghost)
            return ImprovementType.new_1st, 1
        prev_first = top10[0]
        top10.append(new_time)
        times = sorted(top10)

        improvement_type = ImprovementType.improvement
        pos = 4
        found = False
        position = 1
        for i in range(0, len(times)):
            if i != 0 and times[i-1] != times[i]:
                position = i + 1
            if times[i].name == new_time.name:
                if times[i].new:
                    found = True
                    if position == 1:
                        pos = 1
                        if prev_first.name == new_time.name:
                            improvement_type = ImprovementType.improvement_1st
                        else:
                            if prev_first == new_time:
                                improvement_type = ImprovementType.tie_1st
                            else:
                                improvement_type = ImprovementType.new_1st
                    else:
                        if position > 10:
                            return ImprovementType.none, pos
                        pos = position if position < 4 else 4
                else:
                    if found:
                        # reuse variable (kinda cheeky)
                        found = False
                        self.DB.del_top_entry(times[i].ghost, track)
                        del times[i]
                        break
                    else:
                        return ImprovementType.none, pos

        self.DB.insert_top_entry(track, new_time.name, str(new_time.time), new_time.ghost)
        if len(times) > 10:
            if times[9] != times[-1]:
                for i in range(10, len(times)):
                    self.DB.del_top_entry(times[i].ghost, track)
        if found:
            improvement_type = ImprovementType.new
        return improvement_type, pos

    async def update_tops(self, client):
        """Looks for new times"""

        new_times = await self.aq.get_ghosts()
        # returns a list with info about the times that were added
        time_info = list()

        changed = False
        for track in new_times:
            #ignore these categories, they aren't really useful
            if track in ["GCN Waluigi Stadium (Glitch)", "Coconut Mall (Shortcut)", "N64 Bowser's Castle (Alternate)", ""]: continue
            for time in new_times[track]:
                improvement_type, pos = self.add_time(time, track)
                if improvement_type != 0:
                    changed = True
                time_info.append((track, time, improvement_type, pos))

        return time_info, changed

    def get_top_10(self, track):
        """Returns top10 of the given track"""

        times = sorted([Ghost(x[0], x[1], x[2], x[3]) for x in self.DB.get_top10(track)])
        try:
            top10 = [(1, times[0])]
        except IndexError:
            return []

        position = 1
        for i in range(1, len(times)):
            if times[i-1] != times[i]:
                position = i + 1
            top10.append((position, times[i]))

        return top10

    def get_top_10_no_db(self, tops):
        """Returns top10 of the given track"""

        times = sorted([Ghost(x[0], x[1], x[2], x[3]) for x in tops])
        try:
            top10 = [(1, times[0])]
        except IndexError:
            return []

        position = 1
        for i in range(1, len(times)):
            if times[i-1] != times[i]:
                position = i + 1
            top10.append((position, times[i]))

        return top10

    async def update_players(self):
        await self.aq.get_players()

