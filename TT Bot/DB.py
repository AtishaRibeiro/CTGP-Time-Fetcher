import sqlite3
import json
import logging

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
    ("RDKJP NG", "N64 DK's Jungle Parkway", 0),
    ("RDKJP ALT","N64 DK's Jungle Parkway (Shortcut)", 2), #
    ("RDKJP",    "N64 DK's Jungle Parkway (Glitch)", 1),
    ("RMC",      "GCN Mario Circuit", 0),
    ("RMC3",     "SNES Mario Circuit 3", 0),
    ("RPG",      "DS Peach Gardens", 0),
    ("RDKM NG",  "GCN DK Mountain", 0),
    ("RDKM",     "GCN DK Mountain (Shortcut)", 1),
    ("RBC",      "N64 Bowser's Castle", 0),
]

def exception_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logging.critical("Exception occurred", exc_info=True)
    return wrapper


class DB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)

    def cursor(self):
        return self.conn.cursor()

    def create_db(self, new=False):
        curs = self.cursor()
        # create tracks table
        curs.execute("create table if not exists tracks(abbrv text, track_name text primary key, category int)")
        # create personal best table
        curs.execute("create table if not exists personal_bests(player_id text, track text, ghost_hash text, time text, primary key(player_id, track), foreign key(track) references tracks(track_name))")
        # create top10 table
        curs.execute("create table if not exists top10(track text, player_id text, time text, ghost text, primary key(track, ghost), foreign key(track) references tracks(track_name))")
        # create player table
        curs.execute("create table if not exists players(player_id text primary key, player_name text, country text)")
        # create banned times table
        curs.execute("create table if not exists banned_times(ghost_hash text primary key)")

        if new:
            with open("BNL.json") as file:
                data = json.load(file)
                for player in data["Players"]:
                    curs.execute("insert or replace into players values(?, ?, ?)", [player[1], player[2], player[0]])
                for track in data["Tracks"]:
                    for ghost in data["Tracks"][track]:
                        curs.execute("insert or replace into top10 values(?, ?, ?, ?)", [track, ghost["ID"], ghost["Time"], ghost["Ghost"]])

            for track in TRACKS:
                curs.execute("insert or replace into tracks values(?, ?, ?)", track)

        self.conn.commit()

    @exception_catcher
    def reset_track(self, track_name):
        curs = self.cursor()
        curs.execute("delete from top10 where track = ?", [track_name])

        with open("BNL.json") as file:
            data = json.load(file)
            for ghost in data["Tracks"][track_name]:
                curs.execute("insert or replace into top10 values(?, ?, ?, ?)", [track_name, ghost["ID"], ghost["Time"], ghost["Ghost"]])

        self.conn.commit()
        curs.execute("select country, player_name, time, ghost_hash from players natural join (select player_id, time, ghost_hash from personal_bests where track = ?)", [track_name])
        return curs.fetchall()

    @exception_catcher
    def get_ghost_hash(self, player_id, track_name):
        curs = self.cursor()
        curs.execute("select ghost_hash from personal_bests where player_id = ? and track = ?", [player_id, track_name])
        return curs.fetchone()[0]

    @exception_catcher
    def insert_pb(self, player_id, track_name, ghost_hash, time):
        curs = self.cursor()

        #if the ghost is already in the table
        if curs.execute("select exists(select 1 from personal_bests where ghost_hash = ?)", [ghost_hash]).fetchone()[0]:
            return False

        curs.execute("insert or replace into personal_bests values(?, ?, ?, ?)", [player_id, track_name, ghost_hash, time])
        self.conn.commit()
        print("inserted {} - {} - {} - {}".format(track_name, player_id, ghost_hash, time))
        return True

    @exception_catcher
    def get_top10(self, track_name):
        curs = self.cursor()
        curs.execute("select country, player_name, time, ghost from players natural join (select player_id, time, ghost from top10 where track = ?)", [track_name])
        return curs.fetchall()

    @exception_catcher
    def del_top_entry(self, ghost, track):
        curs = self.cursor()
        print("delete {} on {}".format(ghost, track))
        curs.execute("delete from top10 where ghost = ? and track = ?" , [ghost, track])
        self.conn.commit()

    @exception_catcher
    def insert_top_entry(self, track, player_name, time, ghost):
        curs = self.cursor()
        print("inserting top entry {}, {}, {}, {}".format(track, player_name, time, ghost))
        player_id = self.get_player_id(player_name)[0][0]
        curs.execute("insert or replace into top10 values(?, ?, ?, ?)", [track, player_id, time, ghost])
        self.conn.commit()

    @exception_catcher
    def get_track_name(self, abbrv):
        curs = self.cursor()
        curs.execute("select track_name from tracks where abbrv = ?", [abbrv])
        return curs.fetchone()

    @exception_catcher
    def set_player(self, player_id, player_name, country):
        """Adds or updates the player to the players table"""
        curs = self.cursor()
        curs.execute("insert or replace into players values(?, ?, ?)", [player_id, player_name, country])
        self.conn.commit()
        return True

    @exception_catcher
    def remove_player(self, player_id):
        """Remove a player from the the players table if it exists"""
        if self.player_exists(player_id):
            curs = self.cursor()
            curs.execute("delete from players where player_id = ?", [player_id])
            self.conn.commit()
            return True
        return False

    @exception_catcher
    def set_player_name(self, player_id, player_name):
        """Sets the name for an existing player"""
        if self.player_exists(player_id):
            curs = self.cursor()
            curs.execute("update players set player_name = ? where player_id = ?", [player_name, player_id])
            self.conn.commit()
            return True
        return False

    @exception_catcher
    def get_player_count(self, player_name):
        curs = self.cursor()

        tracks = list()
        curs.execute("select player_id from players where lower(player_name) = lower(?)", [player_name])
        for player_id in curs.fetchall():
            curs.execute("select track from top10 where player_id = ?", [player_id[0]])
            tracks.extend(curs.fetchall())
        
        total_count = 0
        ng_count = 0
        glitch_count = 0
        alt_count = 0

        for track in tracks:
            try:
                category = curs.execute("select category from tracks where track_name = ?", track).fetchone()[0]
            except TypeError:
                continue
            if category == 0:
                ng_count += 1
            elif category == 1:
                glitch_count += 1
            elif category == 2:
                alt_count += 1
            total_count += 1

        # get the player name with correct capitalisation
        player_name = curs.execute("select player_name from players where lower(player_name) = lower(?)", [player_name]).fetchone()
        if player_name is not None:
            player_name = player_name[0]

        return player_name, total_count, ng_count, glitch_count, alt_count

    @exception_catcher
    def get_player_info(self, player_id):
        curs = self.cursor()
        curs.execute("select country, player_name from players where player_id = ?", [player_id])
        result = curs.fetchone()
        if result is None:
            return None
        else:
            return result

    @exception_catcher
    def get_player_id(self, player_name):
        curs = self.cursor()
        curs.execute("select player_id from players where lower(player_name) = lower(?)", [player_name])
        return curs.fetchall()

    @exception_catcher
    def player_exists(self, player_id):
        curs = self.cursor()
        return curs.execute("select exists(select 1 from players where player_id = ?)", [player_id]).fetchone()[0]

    @exception_catcher
    def get_player_pb(self, player_id, track):
        curs = self.cursor()
        curs.execute("select player_name, ghost_hash, time from personal_bests natural join players where player_id = ? and track = ?", [player_id, track])
        return curs.fetchone()

    @exception_catcher
    def track_exists(self, track_name):
        curs = self.cursor()
        return curs.execute("select exists(select 1 from tracks where track_name = ?)", [track_name]).fetchone()[0]

    @exception_catcher
    def ban_time(self, ghost_hash):
        curs = self.cursor()
        curs.execute("insert or replace into banned_times values(?)", [ghost_hash])
        self.conn.commit()

    @exception_catcher
    def is_banned(self, ghost_link):
        curs = self.cursor()
        ghost_hash = ghost_link[43:-5]
        ghost_hash = ghost_hash[:2] + ghost_hash[3:5] + ghost_hash[6:]
        return curs.execute("select exists(select 1 from banned_times where ghost_hash = ?)", [ghost_hash]).fetchone()[0]

    @exception_catcher
    def get_all_tops(self):
        curs = self.cursor()
        cups = dict()
        cup = ""
        for i in range(len(TRACKS)):
            track = TRACKS[i]
            top10 = self.get_top10(track[1])
            if i == 0:
                cup = "Mushroom Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 5:
                cup = "Flower Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 12:
                cup = "Star Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 19:
                cup = "Special Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 24:
                cup = "Shell Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 30:
                cup = "Banana Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 35:
                cup = "Leaf Cup"
                cups[cup] = [(track[1], top10)]
            elif i == 43:
                cup = "Lightning Cup"
                cups[cup] = [(track[1], top10)]
            else:
                cups[cup].append((track[1], top10))

        return cups



if __name__ == "__main__":
    database = DB("tt_bot_db.db")
    database.create_db(True)
