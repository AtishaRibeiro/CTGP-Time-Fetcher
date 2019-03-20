import json
import csv
import asyncio
from DB import DB
from datetime import datetime
from GhostFetcher import GhostFetcher
from GhostFetcher import Ghost

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

        # action: 0->not added, 1->time improved, 2->new player, 3->new 1st place, 4->1st place tie
        action = 0
        times = sorted([Ghost(x[0], x[1], x[2], x[3]) for x in self.DB.get_top10(track)])

        if len(times) == 0:
            # return when the track is not kept track of (pun not intended)
            return action

        # check if the time belongs in the top10
        if new_time <= times[-1]:
            action = 2
        else:
            return 0

        # check if the player is already in the top10
        for time in times:
            if new_time.name == time.name:
                if new_time <= time:
                    action = 1
                    times.remove(time)
                    self.DB.del_top_entry(time.ghost, track)
                else:
                    return 0
                break

        if new_time < times[0]:
            action = 3
        elif new_time == times[0] and action is not 1:
            action = 4

        times.insert(0, new_time)

        # remove times that fall out of the top10
        # check the count in case of a tie at tenth place
        if len(set(times)) > 10:
            amount = times.count(max(times))
            for i in range(len(times)-1, len(times)-amount-1, -1):
                self.DB.del_top_entry(times[i].ghost, track)

        self.DB.insert_top_entry(track, new_time.country, new_time.name, str(new_time.time), new_time.ghost)

        return action

    async def update_tops(self, client):
        """Looks for new times"""

        gf = GhostFetcher(self.countries, client, self.DB)
        new_times = await gf.get_ghosts()
        # returns a list with info about the times that were added
        time_info = list()

        changed = False
        for track in new_times:
            #ignore these categories, they aren't really useful
            if track in ["GCN Waluigi Stadium (Glitch)", "Coconut Mall (Shortcut)", "N64 Bowser's Castle (Alternate)"]: continue
            for time in new_times[track]:
                action = self.add_time(time, track)
                if action != 0:
                    changed = True
                time_info.append((track, time, action))

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