import json
import csv
from datetime import datetime
from GhostFetcher import GhostFetcher
from GhostFetcher import Ghost

class Tops:

    """Commented constructor used to get the BNL times from csv file (hardcoded!)"""

    # def __init__(self, filename):
    #     self.countries = ['🇧🇪','🇳🇱','🇱🇺'];
    #     self.tracks = dict()

    #     with open(filename) as csv_file:
    #         csv_reader = csv.reader(csv_file, delimiter=',')
    #         line_count = 0
    #         tracks = list()
    #         track_nr = 0
    #         for row in csv_reader:
    #             print(row)
    #             try:
    #                 dummy = int(row[0])

    #                 for i in range(len(tracks)):
    #                     if len(row[i*5+3]) == 0:
    #                         entry = Ghost({
    #                             "Country": "row[i*5+1]",
    #                             "Name": "Dummy",
    #                             "Time": "01:00.000",
    #                             "Ghost": row[i*5+4]})
    #                         self.tracks[tracks[i]].append(entry)
    #                     else:
    #                         entry = Ghost({
    #                             "Country": row[i*5+1],
    #                             "Name": row[i*5+2],
    #                             "Time": row[i*5+3],
    #                             "Ghost": row[i*5+4]})
    #                         self.tracks[tracks[i]].append(entry)

    #             except ValueError:
    #                 tracks = row
    #                 for track in tracks:
    #                     self.tracks[track] = list()

    #             line_count += 1

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
        # action: 0->not added, 1->time improved, 2->new player, 3->new 1st place, 4->1st place tie
        action = 0
        times = sorted(self.tracks[track])

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
        elif new_time == times[0]:
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
        print([str(x) for x in self.tracks[track]])
        return action

    def update_tops(self, cmp_date):
        gf = GhostFetcher()
        new_times = gf.get_ghosts(self.countries, cmp_date)

        for track, time in new_times.items():
            self.add_time(time, track)


if __name__ == "__main__":
    tops = Tops("BeNeLux-Leaderboards-No-Glitch.csv")
    tops.write_json("BNL.json")