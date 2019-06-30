import json
import csv
import asyncio
from DB import DB
from datetime import datetime
from GhostFetcher import GhostFetcher
from GhostFetcher import Ghost
import sys
from enum import Enum

class ImprovementType(Enum):
    none = 0
    improvement = 1
    new = 2
    new_1st = 3
    tie_1st = 4
    improvement_1st = 5

class Tops:
    """Class that handles the topX of a region"""

    def __init__(self, db):
        self.countries = [67, 88, 94]
        self.DB = db

    def write_json(self, filename):
        """write the contents of self.tracks to (filename)"""

        data = {}
        data["Info"] = {
            "Countries": self.countries,
        }
        data["Tracks"] = dict()

        for track in self.tracks:
            data["Tracks"][track] = list()
        for track, times in self.tracks.items():
            for time in times:
                data["Tracks"][track].append(time.to_dict())

        with open(filename, "w") as outfile:
            json.dump(data, outfile, indent=4)

    def add_time(self, new_time, track):
        """Attempts to add 'new_time' to the top10, only adds if it belongs there"""

        action = ImprovementType.new
        times = sorted([Ghost(x[0], x[1], x[2], x[3]) for x in self.DB.get_top10(track)])

        sys.stdout.flush()
        if self.DB.is_banned(new_time.ghost):
            return ImprovementType.none, 4

        # in case the top10 is empty
        if times is None or len(times) == 0:
            self.DB.insert_top_entry(track, new_time.country, new_time.name, str(new_time.time), new_time.ghost)
            return ImprovementType.new_1st, 1

        if len(set(times)) == 10:
            # check if the time belongs in the top10
            if new_time > times[-1]:
                return ImprovementType.none, 4

        # check if the player is already in the top10
        for time in times:
            if new_time.name == time.name:
                if new_time <= time:
                    action = 1
                    times.remove(time)
                    self.DB.del_top_entry(time.ghost, track)
                else:
                    return ImprovementType.none, 4
                break

        if len(times) > 0:
            if new_time < times[0]:
                if times[0].name == new_time.name:
                    action = ImprovementType.improvement_1st
                action = ImprovementType.new_1st
            elif new_time == times[0] and action is not ImprovementType.improvement:
                action = ImprovementType.tie_1st
        else:
            action = ImprovementType.new_1st

        # sort the times
        times.append(new_time)
        times = sorted(times)

        # check position in top3 (if it's there)
        pos = 1
        time_index = 0
        while pos < 4:
            current_time = times[time_index]
            if time == current_time:
                break
            else:
                time_index += 1
                if times[time_index] > current_time:
                    pos += 1

        # remove times that fall out of the top10
        # check the count in case of a tie at tenth place
        if len(set(times)) > 10:
            amount = times.count(max(times))
            for i in range(len(times)-amount, len(times)):
                self.DB.del_top_entry(times[i].ghost, track)

        self.DB.insert_top_entry(track, new_time.country, new_time.name, str(new_time.time), new_time.ghost)

        return action, pos

    async def update_tops(self, client):
        """Looks for new times"""

        gf = GhostFetcher(self.countries, client, self.DB)
        new_times = await gf.get_ghosts()
        # new_times = {"Wario's Gold Mine": [Ghost("🇳🇱", "Weexy", "01:52.781", "http://www.chadsoft.co.uk/time-trials/rkgd/61/97/73B7181F9D758A7CBB2B579501B69E98C0C7.html")]}
        # returns a list with info about the times that were added
        time_info = list()

        changed = False
        for track in new_times:
            #ignore these categories, they aren't really useful
            if track in ["GCN Waluigi Stadium (Glitch)", "Coconut Mall (Shortcut)", "N64 Bowser's Castle (Alternate)"]: continue
            for time in new_times[track]:
                action, pos = self.add_time(time, track)
                if action != 0:
                    changed = True
                time_info.append((track, time, action, pos))

        return time_info, changed

    def get_top_10(self, track):
        """Returns top10 of the given track"""

        times = sorted([Ghost(x[0], x[1], x[2], x[3]) for x in self.DB.get_top10(track)])
        top10 = [(1, times[0])]

        position = 1
        for i in range(1, len(times)):
            if times[i-1] != times[i]:
                position += 1
            top10.append((position, times[i]))

        return top10


if __name__ == "__main__":
    #tops = Tops("BeNeLux-Leaderboards-No-Glitch.csv")
    #tops.write_json("BNL.json")
    pass