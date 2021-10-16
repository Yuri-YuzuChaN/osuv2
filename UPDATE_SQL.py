import sqlite3, os

old = os.path.expanduser('~/.hoshino/osu.db')

class UserSQL:

    def __init__(self):
        self.makeuser()
        self.makeinfo()
        self.user_update()
        self.info_update()
        self.delsql()

    def old_conn(self):
        return sqlite3.connect(old)

    def makeuser(self):
        try:
            self.old_conn().execute('''CREATE TABLE USER(
                ID      INTEGER         PRIMARY KEY     NOT NULL,
                QQID    INTEGER         NOT NULL,
                OSUID   INTEGER         NOT NULL,
                OSUNAME TEXT            NOT NULL,
                OSUMODE INTEGER         NOT NULL
                )''')
        except sqlite3.OperationalError:
            pass

    def makeinfo(self):
        try:
            self.old_conn().execute('''CREATE TABLE INFO(
                ID          INTEGER         PRIMARY KEY     NOT NULL,
                OSUID       INTEGER         NOT NULL,
                C_RANKED    INTEGER         NOT NULL,
                G_RANKED    INTEGER         NOT NULL,
                PP          REAL            NOT NULL,
                ACC         REAL            NOT NULL,
                PC          INTEGER         NOT NULL,
                COUNT       INTEGER         NOT NULL,
                OSUMODE     INTEGER         NOT NULL
            )''')
        except sqlite3.OperationalError:
            pass

    def user_update(self):
        try:
            oldinfo = self.old_conn().execute('SELECT * FROM userinfo').fetchall()
            for i in oldinfo:
                self.user_insert(i[1], i[2], i[3])
        except:
            print('sss')

    def user_insert(self, qqid: int, id: int, name: str):
        try:
            conn = self.old_conn()
            conn.execute(f'INSERT INTO USER VALUES (NULL, {qqid}, {id}, "{name}", 0)')
            conn.commit()
        except Exception as e:
            print('sss')

    def info_update(self):
        user = self.old_conn().execute('SELECT * FROM newinfo').fetchall()
        for i in user:
            self.info_insert(i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
    
    def info_insert(self, id: int, c_ranked: int, g_ranked: int, pp: int, acc: int, pc: int, count: int, mode: int):
        conn = self.old_conn()
        conn.execute(f'INSERT INTO INFO VALUES (NULL, {id}, {c_ranked}, {g_ranked}, {pp}, {acc}, {pc}, {count}, {mode})')
        conn.commit()

    def delsql(self):
        self.old_conn().execute('DROP TABLE userinfo')
        self.old_conn().execute('DROP TABLE newinfo')

UserSQL()
