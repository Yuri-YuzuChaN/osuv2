import sqlite3, os
from typing import Tuple, Union
from hoshino.log import new_logger

SQL = os.path.expanduser('~/.hoshino/osu.db')
logger = new_logger('osuv2_SQL')

class UserSQL:

    def __init__(self):
        self.makeuser()
        self.makeinfo()

    def conn(self):
        return sqlite3.connect(SQL)

    def makeuser(self):
        try:
            self.conn().execute('''CREATE TABLE USER(
                ID      INTEGER         PRIMARY KEY     NOT NULL,
                QQID    INTEGER         NOT NULL,
                OSUID   INTEGER         NOT NULL,
                OSUNAME TEXT            NOT NULL,
                OSUMODE INTEGER         NOT NULL
                )''')
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            logger.error(e)

    def makeinfo(self):
        try:
            self.conn().execute('''CREATE TABLE INFO(
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
        except Exception as e:
            logger.error(e)

    def get_user(self, qqid: int) -> Union[tuple, bool]:
        '''
        获取玩家信息，返回元组 `id`, `name`, `mode`
        '''
        try:
            result = self.conn().execute(f'SELECT OSUID, OSUNAME, OSUMODE FROM USER WHERE QQID = {qqid}').fetchall()
            if not result:
                return False
            else:
                return result[0]
        except Exception as e:
            logger.error(e)

    def get_info(self, id: int, mode: int) -> Union[tuple, bool]:
        '''
        获取玩家游玩信息，返回元组
        '''
        try:
            result = self.conn().execute(f'SELECT * FROM INFO WHERE OSUID = {id} and OSUMODE = {mode}').fetchall()
            if not result:
                return False
            else:
                return result[0][2:-1]
        except Exception as e:
            logger.error(e)
            return False

    def get_user_osuid(self) -> Tuple:
        '''
        获取所有玩家 `OSUID`
        '''
        try:
            result = self.conn().execute(f'SELECT OSUID FROM USER').fetchall()
            return result
        except Exception as e:
            logger.error(e)
            return False

    def insert_user(self, qqid: int, id: int, name: str):
        try:
            conn = self.conn()
            conn.execute(f'INSERT INTO USER VALUES (NULL, {qqid}, {id}, "{name}", 0)')
            conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False
    
    def insert_info(self, id: int, c_ranked: int, g_ranked: int, pp: int, acc: int, pc: int, count: int, mode: int):
        try:
            conn = self.conn()
            conn.execute(f'INSERT INTO INFO VALUES (NULL, {id}, {c_ranked}, {g_ranked}, {pp}, {acc}, {pc}, {count}, {mode})')
            conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False

    def update_mode(self, qqid: int, mode: int):
        try:
            conn = self.conn()
            conn.execute(f'UPDATE USER SET OSUMODE = {mode} WHERE QQID = {qqid}')
            conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False

    def update_info(self, id: int, c_ranked: int, g_ranked: int, pp: int, acc: int, pc: int, count: int, mode: int):
        try:
            conn = self.conn()
            conn.execute(f'UPDATE INFO SET C_RANKED = {c_ranked}, G_RANKED = {g_ranked}, PP = {pp}, ACC = {acc}, PC = {pc}, COUNT = {count} where OSUID = {id} and OSUMODE = {mode}')
            conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False

    def delete_user(self, qqid: int):
        try:
            conn = self.conn()
            conn.execute(f'DELETE FROM USER WHERE QQID = {qqid}')
            conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False

    def delete_info(self, id: int):
        try:
            conn = self.conn()
            conn.execute(f'DELETE FROM INFO WHERE OSUID = {id}')
            conn.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False
