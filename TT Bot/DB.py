import sqlite3
import json

class DB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)

    def cursor(self):
        return self.conn.cursor()

    def create_db(self):
        curs = self.cursor()
        # create tracks table
        curs.execute("create table if not exists tracks(track_name text primary key)")
        # create personal best table
        curs.execute("create table if not exists personal_bests(player_id text, track text, ghost_hash text, primary key(player_id, track), foreign key(track) references tracks(track_name))")
        # create top10 table
        curs.execute("create table if not exists top10(track text, country text, name text, time text, ghost text, primary key(track, ghost), foreign key(track) references tracks(track_name))")

        with open("BNL.json") as file:
            data = json.load(file)
            tracks = dict()
            for track in data["Tracks"]:
                curs.execute("insert or replace into tracks values(?)", [track])
                for ghost in data["Tracks"][track]:
                    #print("{}\n{}".format(track, ghost))
                    curs.execute("insert or replace into top10 values(?, ?, ?, ?, ?)", [track, ghost["Country"], ghost["Name"], ghost["Time"], ghost["Ghost"]])

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


if __name__ == "__main__":
    database = DB("tt_bot_db.db")
    database.create_db()
