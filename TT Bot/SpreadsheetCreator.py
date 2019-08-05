import sqlite3
import json
from DB import DB
from GhostFetcher import Ghost

def get_top_10_no_db(tops):
        """Returns top10 of the given track"""

        times = sorted([Ghost(x[0], x[1], x[2], x[3]) for x in tops])
        top10 = [(1, times[0])]

        position = 1
        for i in range(1, len(times)):
            if times[i-1] != times[i]:
                position += 1
            top10.append((position, times[i]))

        return top10

if __name__ == "__main__":
    DB = DB("tt_bot_db.db")
    tops = DB.get_all_tops()

    file = open("tops.csv", "w")

    for cup in tops:
        file.write("{}\n\n".format(cup))
        
        for track in tops[cup]:
            trackname = track[0]
            file.write("{}\n".format(trackname))
            
            sorted_tops = get_top_10_no_db(track[1])
            for pos, time in sorted_tops:
                    pos_str = str(pos)
                    file.write("{},{},{},{},{}\n".format(pos_str, time.country, time.name, time.time, time.ghost))
            file.write("\n")

    file.close()
