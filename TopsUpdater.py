import json
import csv
import asyncio
from datetime import datetime
from GhostFetcher import GhostFetcher
from GhostFetcher import Ghost

class Tops:
    """Class that handles the topX of a region"""

    def __init__(self, filename):
        with open(filename) as file:
            data = json.load(file)
            self.countries = data["Info"]["Countries"]

            self.tracks = dict()
            for track in data["Tracks"]:
                self.tracks[track] = list()
            for track, times in data["Tracks"].items():
                for time in times:
                    self.tracks[track].append(Ghost(time))

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
        try:
            times = sorted(self.tracks[track])
        except KeyError:
            # error gets thrown when the track is not kept track of (pun not intended)
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
                    print("name found")
                else:
                    return 0
                break

        if new_time < times[0]:
            action = 3
        elif new_time == times[0] and action is not 1:
            action = 4
        times.insert(0, new_time)

        # remove times that fall out of the top10
        new_tops = [times[0]]
        places = 0
        for time in times[1:]:
            if time != new_tops[-1]:
                places += 1
            if places > 10:
                break
            new_tops.append(time)

        self.tracks[track] = sorted(new_tops)
        return action

    async def update_tops(self, cmp_date):
        """Looks for times that were set starting from 'cmp_date'"""

        gf = GhostFetcher(self.countries)
        new_times = await gf.get_ghosts(cmp_date)
        # returns a list with info about the times that were added
        time_info = list()

        for track in new_times:
            #ignore these categories, they aren't really useful
            if track in ["GCN Waluigi Stadium (Glitch)", "Coconut Mall (Shortcut)", "N64 Bowser's Castle (Alternate)"]: continue
            for time in new_times[track]:
                action = self.add_time(time, track)
                if action != 0:
                    time_info.append((track, time, action))

        return time_info


    def get_top_10(self, track):
        """Returns top10 of the given track"""

        times = sorted(self.tracks[track])
        top10 = [(1, times[0])]

        position = 1
        for i in range(1, len(times)):
            if times[i-1] != times[i]:
                position += 1
            top10.append((position, times[i]))

        return top10


if __name__ == "__main__":
    tops = Tops("BeNeLux-Leaderboards-No-Glitch.csv")
    tops.write_json("BNL.json")