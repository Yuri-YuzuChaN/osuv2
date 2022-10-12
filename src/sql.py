import sqlite3, os
from typing import Tuple, Union

from .error import *
from . import *

SQL = os.path.expanduser('~/.hoshino/osu.db')

class UserSQL:

    def __init__(self):
        self.make_user_db()
        self.make_user_play_db()

    def conn(self):
        return sqlite3.connect(SQL)

    def make_user_db(self):
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
            sv.logger.error(e)

    def make_user_play_db(self):
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
            sv.logger.error(e)

    def get_user_info(self, qqid: int) -> Union[Tuple[int, str, int], bool]:
        '''
        获取玩家数据
        '''
        result = self.conn().execute(f'SELECT OSUID, OSUNAME, OSUMODE FROM USER WHERE QQID = {qqid}').fetchall()
        if not result:
            raise UserNotBindError
        else:
            return result[0]

    def get_user_play_info(self, id: int, mode: int) -> Union[Tuple[Union[str, int]], bool]:
        '''
        获取玩家游玩数据
        '''
        try:
            result = self.conn().execute(f'SELECT * FROM INFO WHERE OSUID = {id} and OSUMODE = {mode}').fetchall()
            if not result:
                return False
            else:
                return result[0][2:-1]
        except Exception as e:
            sv.logger.error(e)
            return False

    def get_user_osuid(self) -> Tuple:
        '''
        获取所有玩家的 `OSUID`
        '''
        try:
            result = self.conn().execute(f'SELECT OSUID FROM USER').fetchall()
            return result
        except Exception as e:
            sv.logger.error(e)
            return False

    def insert_user_info(self, qqid: int, id: int, name: str, mode: int):
        """
        添加新绑定玩家
        """
        try:
            conn = self.conn()
            conn.execute(f'INSERT INTO USER VALUES (NULL, {qqid}, {id}, "{name}", {mode})')
            conn.commit()
            return True
        except Exception as e:
            sv.logger.error(e)
            return False
    
    def insert_user_play_info(self, id: int, c_ranked: int, g_ranked: int, pp: int, acc: int, pc: int, count: int, mode: int):
        """
        添加新绑定玩家游玩数据
        """
        try:
            conn = self.conn()
            conn.execute(f'INSERT INTO INFO VALUES (NULL, {id}, {c_ranked}, {g_ranked}, {pp}, {acc}, {pc}, {count}, {mode})')
            conn.commit()
            return True
        except Exception as e:
            sv.logger.error(e)
            return False

    def update_user_mode(self, qqid: int, mode: int):
        """
        更改玩家默认查询模式
        """
        try:
            conn = self.conn()
            conn.execute(f'UPDATE USER SET OSUMODE = {mode} WHERE QQID = {qqid}')
            conn.commit()
            return True
        except Exception as e:
            sv.logger.error(e)
            return False

    def update_user_play_info(self, id: int, c_ranked: int, g_ranked: int, pp: int, acc: int, pc: int, count: int, mode: int):
        """
        更新玩家游玩数据
        """
        try:
            conn = self.conn()
            conn.execute(f'UPDATE INFO SET C_RANKED = {c_ranked}, G_RANKED = {g_ranked}, PP = {pp}, ACC = {acc}, PC = {pc}, COUNT = {count} where OSUID = {id} and OSUMODE = {mode}')
            conn.commit()
            return True
        except Exception as e:
            sv.logger.error(e)
            return False

    def delete_user(self, qqid: int):
        """
        删除绑定玩家
        """
        try:
            conn = self.conn()
            conn.execute(f'DELETE FROM USER WHERE QQID = {qqid}')
            conn.commit()
            return True
        except Exception as e:
            sv.logger.error(e)
            return False

    def delete_user_info(self, id: int):
        """
        删除绑定玩家游玩数据
        """
        try:
            conn = self.conn()
            conn.execute(f'DELETE FROM INFO WHERE OSUID = {id}')
            conn.commit()
            return True
        except Exception as e:
            sv.logger.error(e)
            return False

USER = UserSQL()