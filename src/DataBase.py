from datetime import datetime, timedelta
from typing import List, Optional

from peewee import *

from .. import OsuDataBase
from .Error import *
from .Model import User as _User

db = SqliteDatabase(OsuDataBase)


class OsuModel(Model):
    class Meta:
        database = db


class User(OsuModel):
    ID = IntegerField(primary_key=True)
    Qqid = BigIntegerField()
    Osuid = BigIntegerField()
    Osuname = TextField()
    Osumode = IntegerField()

    class Meta:
        table_name = 'User'


class ModeData(OsuModel):
    Osuid = BigIntegerField()
    CountryRanked = BigIntegerField()
    GlobalRanked = BigIntegerField()
    Pp = FloatField()
    Accuracy = FloatField()
    PlayCount = BigIntegerField()
    Hit = BigIntegerField()
    DateTime = DateTimeField(default=datetime.now() + timedelta(days=-1))


class StdMode(ModeData):
    class Meta:
        table_name = 'Std'


class TaikoMode(ModeData):
    class Meta:
        table_name = 'Taiko'


class CtbMode(ModeData):
    class Meta:
        table_name = 'Ctb'


class ManiaMode(ModeData):
    class Meta:
        table_name = 'Mania'


DatabaseTable = [User, StdMode, TaikoMode, CtbMode, ManiaMode]
ModeTable: List[ModeData] = DatabaseTable[1:]


db.create_tables(DatabaseTable)


def get_user_data(qqid: int) -> Optional[User]:
    record: Select = User.select().where(User.Qqid == qqid)
    if record:
        return record.get()
    else:
        raise UserNotBindError


def get_all_user_osuid() -> List[User]:
    return list(User.select(User.Osuid))


def get_user_daily_data(osuid: int, day: int = 0, mode: int = 0) -> Optional[ModeData]:
    time = datetime.now() - timedelta(day)
    table = ModeTable[mode]
    record: Select = table.select().where((table.Osuid == osuid) & (table.DateTime == time))
    if record:
        return record.get()
    return None


def insert_user(qqid: int, user: _User) -> bool:
    try:
        User.insert(Qqid=qqid, Osuid=user.id, Osuname=user.username, Osumode=user.play_mode).execute()
        return True
    except:
        return False


def insert_user_daily_data(mode: int, data: List[_User]) -> bool:
    try:
        table = ModeTable[mode]
        dbdata = [(d.id, 
            d.statistics.country_rank, 
            d.statistics.global_rank, 
            d.statistics.pp,
            d.statistics.accuracy,
            d.statistics.play_count,
            d.statistics.total_hits) for d in data]
        with db.atomic():
            for i in range(0, len(data), 100):
                table.insert_many(dbdata[i:i + 100], ['Osuid', 'CountryRanked', 'GlobalRanked', 'Pp', 'Accuracy', 'PlayCount', 'Hit']).execute()   
        return True
    except:
        return False


def update_user_mode(qqid: int, mode: int) -> bool:
    try:
        User.update(User.Osumode == mode).where(User.Qqid == qqid)
        return True
    except:
        return False


def delete_user(qqid: int) -> bool:
    try:
        User.delete().where(User.Qqid == qqid).execute()
        return True
    except:
        return False