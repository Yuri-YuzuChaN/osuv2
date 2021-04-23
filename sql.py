import sqlite3
import os

SQL = os.path.expanduser('~/.hoshino/osu.db')

class osusql():
    def __init__(self):
        os.makedirs(os.path.dirname(SQL), exist_ok=True)
        self.makesql()
        self.makeinfo()

    def con(self):
        return sqlite3.connect(SQL)

    def makesql(self):
        try:
            self.con().execute('''CREATE TABLE userinfo(
                id      INTEGER         PRIMARY KEY     NOT NULL,
                qqid    INTEGER         NOT NULL,
                osuid   INTEGER         NOT NULL,
                osuname TEXT            NOT NULL,
                osumod  INTEGER         NOT NULL
                )''')
        except Exception as e:
            print(e)

    def makeinfo(self):
        try:
            self.con().execute('''CREATE TABLE newinfo(
                id          INTEGER         PRIMARY KEY     NOT NULL,
                osuid       INTEGER         NOT NULL,
                c_ranked    INTEGER         NOT NULL,
                g_ranked    INTEGER         NOT NULL,
                pp          REAL            NOT NULL,
                acc         REAL            NOT NULL,
                pc          INTEGER         NOT NULL,
                count       INTEGER         NOT NULL,
                osumod      INTEGER         NOT NULL
            )''')
        except Exception as e:
            print(e)

    def get_name_mod(self, uid):
        try:
            result = self.con().execute(f'select osuname, osumod from userinfo where qqid = {uid}').fetchall()
            return result
        except Exception as e:
            print(e)
    
    def get_id_mod(self, uid):
        try:
            result = self.con().execute(f'select osuid, osumod from userinfo where qqid = {uid}').fetchall()
            return result
        except Exception as e:
            print(e)

    def get_all_id(self):
        try:
            result = self.con().execute('select osuid from userinfo').fetchall()
            return result
        except Exception as e:
            print(e)
            return False
        
    def get_all_newinfo(self, uid, osumod):
        try:
            result = self.con().execute(f'select * from newinfo where osuid = {uid} and osumod = {osumod}').fetchall()
            return result
        except Exception as e:
            print(e)
            return False

    def insert_user(self, uid, osuid, osuname):
        try:
            con = self.con()
            con.execute(f'insert into userinfo values (NULL, {uid}, {osuid}, "{osuname}", 0)')
            con.commit()
            return True
        except Exception as e:
            print(e)
            return False
    
    def insert_all_info(self, uid, c_ranked, g_ranked, pp, acc, pc, count, osumod):
        try:
            con = self.con()
            con.execute(f'insert into newinfo values (NULL, {uid}, {c_ranked}, {g_ranked}, {pp}, {acc}, {pc}, {count}, {osumod})')
            con.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def update_mode(self, uid, osumod):
        try:
            con = self.con()
            con.execute(f'update userinfo set osumod = {osumod} where qqid = {uid}')
            con.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def update_all_info(self, uid, c_ranked, g_ranked, pp, acc, pc, count, osumod):
        try:
            con = self.con()
            con.execute(f'update newinfo set c_ranked = {c_ranked}, g_ranked = {g_ranked}, pp = {pp}, acc = {acc}, pc = {pc}, count = {count} where osuid = {uid} and osumod = {osumod}')
            con.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete_user(self, uid):
        try:
            con = self.con()
            con.execute(f'delete from userinfo where qqid = {uid}')
            con.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def delete_newinfo(self, uid):
        try:
            con = self.con()
            con.execute(f'delete from newinfo where osuid = {uid}')
            con.commit()
            return True
        except Exception as e:
            print(e)
            return False