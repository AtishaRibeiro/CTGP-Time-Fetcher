import sqlite3
import json

TRACKS = [
    ("LC",       "Luigi Circuit", 0),
    ("MMM",      "Moo Moo Meadows", 0),
    ("MG NG",    "Mushroom Gorge", 0),
    ("MG",       "Mushroom Gorge (Glitch)", 1),
    ("TF",       "Toad's Factory", 0),
    ("MC NG",    "Mario Circuit", 0),
    ("MC",       "Mario Circuit (Glitch)", 1),
    ("CM NG",    "Coconut Mall", 0),
    ("CM",       "Coconut Mall (Glitch)", 1),
    ("DKS",      "DK Summit", 0),
    ("WGM NG",   "Wario's Gold Mine", 0),
    ("WGM",      "Wario's Gold Mine (Glitch)", 1),
    ("DC",       "Daisy Circuit", 0),
    ("KC",       "Koopa Cape", 0),
    ("MT NG",    "Maple Treeway", 0),
    ("MT",       "Maple Treeway (Glitch)", 1),
    ("GV NG",    "Grumble Volcano", 0),
    ("GV ALT",   "Grumble Volcano (Shortcut)", 2), #
    ("GV",       "Grumble Volcano (Glitch)", 1),
    ("DDR",      "Dry Dry Ruins", 0),
    ("MH",       "Moonview Highway", 0),
    ("BC NG",    "Bowser's Castle", 0),
    ("BC",       "Bowser's Castle (Shortcut)", 1),
    ("RR",       "Rainbow Road", 0),
    ("RPB NG",   "GCN Peach Beach", 0),
    ("RPB",      "GCN Peach Beach (Glitch)", 1),
    ("RYF",      "DS Yoshi Falls", 0),
    ("RGV2 NG",  "SNES Ghost Valley 2", 0),
    ("RGV2",     "SNES Ghost Valley 2 (Glitch)", 1),
    ("RMR",      "N64 Mario Raceway", 0),
    ("RSL NG",   "N64 Sherbet Land", 0),
    ("RSL",      "N64 Sherbet Land (Glitch)", 1),
    ("RSGB",     "GBA Shy Guy Beach", 0),
    ("RDS",      "DS Delfino Square", 0),
    ("RWS",      "GCN Waluigi Stadium", 0),
    ("RDH NG",   "DS Desert Hills", 0),
    ("RDH",      "DS Desert Hills (Shortcut)", 1),
    ("RBC3 NG",  "GBA Bowser Castle 3", 0),
    ("RBC3",     "GBA Bowser Castle 3 (Shortcut)", 1),
    ("RDKJP NG", "N64 DK Jungle Parkway", 0),
    ("RDKJP ALT","N64 DK Jungle Parkway (Shortcut)", 2), #
    ("RDKJP",    "N64 DK Jungle Parkway (Glitch)", 1),
    ("RMC",      "GCN Mario Circuit", 0),
    ("RMC3",     "SNES Mario Circuit 3", 0),
    ("RPG",      "DS Peach Gardens", 0),
    ("RDKM NG",  "GCN DK Mountain", 0),
    ("RDKM",     "GCN DK Mountain (Shortcut)", 1),
    ("RBC",      "N64 Bowser's Castle", 0),
]

class DB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)

    def cursor(self):
        return self.conn.cursor()

    def create_db(self):
        curs = self.cursor()
        # create tracks table
        curs.execute("create table if not exists tracks(abbrv text, track_name text primary key, category int)")
        # create personal best table
        curs.execute("create table if not exists personal_bests(player_id text, track text, ghost_hash text, primary key(player_id, track), foreign key(track) references tracks(track_name))")
        # create top10 table
        curs.execute("create table if not exists top10(track text, country text, name text, time text, ghost text, primary key(track, ghost), foreign key(track) references tracks(track_name))")

        with open("BNL.json") as file:
            data = json.load(file)
            tracks = dict()
            for track in data["Tracks"]:
                for ghost in data["Tracks"][track]:
                    #print("{}\n{}".format(track, ghost))
                    curs.execute("insert or replace into top10 values(?, ?, ?, ?, ?)", [track, ghost["Country"], ghost["Name"], ghost["Time"], ghost["Ghost"]])

        for track in TRACKS:
            curs.execute("insert or replace into tracks values(?, ?, ?)", track)

        self.conn.commit()

    def get_ghost_hash(self, player_id, track_name):
        curs = self.conn.cursor()
        curs.execute("select ghost_hash from personal_bests where player_id = ? and track = ?", [player_id, track_name])
        return curs.fetchone()[0]

    def insert_pb(self, player_id, track_name, ghost_hash):
        curs = self.cursor()

        #if the ghost is already in the table
        if curs.execute("select exists(select 1 from personal_bests where ghost_hash = ?)", [ghost_hash]).fetchone()[0]:
            return False

        curs.execute("insert or replace into personal_bests values(?, ?, ?)", [player_id, track_name, ghost_hash])
        self.conn.commit()
        print("inserted {} - {} - {}".format(player_id, track_name, ghost_hash))
        return True

    def get_top10(self, track_name):
        curs = self.cursor()
        curs.execute("select country, name, time, ghost from top10 where track = ?", [track_name])
        return curs.fetchall()

    def del_top_entry(self, ghost, track):
        curs = self.cursor()
        curs.execute("delete from top10 where ghost = ? and track = ?" , [ghost, track])
        self.conn.commit()

    def insert_top_entry(self, track, country, name, time, ghost):
        curs = self.cursor()
        curs.execute("insert or replace into top10 values(?, ?, ?, ?, ?)", [track, country, name, time, ghost])
        self.conn.commit()

    def get_track_name(self, abbrv):
        curs = self.cursor()
        curs.execute("select track_name from tracks where abbrv = ?", [abbrv])
        return curs.fetchone()[0]

    def get_player_count(self, player_name):
        curs = self.cursor()
        curs.execute("select track from top10 where name = ?", [player_name])
        tracks = curs.fetchall()
        total_count = len(tracks)
        ng_count = 0
        glitch_count = 0
        alt_count = 0

        for track in tracks:
            category = curs.execute("select category from tracks where track_name = ?", track).fetchone()[0]
            if category == 0:
                ng_count += 1
            elif category == 1:
                glitch_count += 1
            elif category == 2:
                alt_count += 1

        return total_count, ng_count, glitch_count, alt_count


if __name__ == "__main__":
    database = DB("tt_bot_db.db")
    database.create_db()
