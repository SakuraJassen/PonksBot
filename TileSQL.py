import asyncio
import datetime
import re
import datetime
from enum import IntFlag, auto, unique

@unique
class TileType(IntFlag):
    EMPTY = auto()
    RELIC = auto()
    BANNER = auto()
    ENEMY = auto()
    NEUTRAL = auto()
    OURS = auto()
    MESSAGE = auto()

    @staticmethod
    async def toString(flag):
        s = ""
        if isinstance(flag, int):
            flag = TileType(flag)
        if isinstance(flag, TileType):
            if flag is not TileType.EMPTY:
                if flag.name is not None:
                    s = flag.name.capitalize()
                else:
                    for f in list(TileType):
                        if (f & flag) > 0:
                            s += f"{f.name.capitalize()}, "
        return s[:-2]


class TileClass:
    refreshTimer: datetime.datetime

    def __init__(self, db, TileCode, TileURL="", tt=TileType.EMPTY, TileMSG="", MSGID=None,
                 TurnsNeutral=datetime.datetime.now(), ForceUpdate=False, LastUpdate=datetime.datetime.now(), channel=None):
        self.db = db
        self.id = TileCode
        self.url = TileURL
        self.type = tt
        self.msg = TileMSG
        self.msg_id = MSGID
        self.message = None
        self.refreshTimer = TurnsNeutral
        self.shouldUpdate = ForceUpdate
        self.lastUpdate = LastUpdate

    def toString(self):
        return (f"TileCode = {self.id} \n" \
                f"TileURL = {self.url} \n" \
                f"tt = {self.type} \n" \
                f"TileMSG = {self.msg} \n" \
                f"MSGID = {self.message} \n" \
                f"TurnsNeutral = {self.refreshTimer} \n" \
                f"ForceUpdate = {self.shouldUpdate} \n" \
                f"LastUpdate = {self.lastUpdate} \n")


async def parseMSG(msg):
    parsed = re.search('.*?: (.*?) \| Expires.*: (.*)', msg)
    if parsed is None:
        parsed2 = re.search('.*?: (.*?) \| .*', msg)
        if parsed2 is None:
            return None
        return parsed2
    return parsed


async def formateMSG(t: TileClass):
    t.lastUpdate = datetime.datetime.now()
    ts = t.refreshTimer - datetime.datetime.now()
    s = ts.seconds + ts.days * 24 * 60 * 60
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    tileProps = await TileType.toString(t.type)
    if hours >= 24:
        expAt = t.refreshTimer.strftime('%d.%m - %H:%M:%S')
    else:
        expAt = t.refreshTimer.strftime('%d.%m - %H:%M:%S')

    if ts.total_seconds() > 0:
        expIn = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        return f"{tileProps} Tile: {t.id} | Expires at: {expAt} | Remaining Time: {expIn}"
    else:
        return f"{tileProps} Tile: {t.id} | Expires at: {expAt} | Expired"

async def createOrUpdateNewTile(db, tc: TileClass):
    add_tile = ("INSERT INTO Tile "
                "(TileCode, TileURL, TileType, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate) "
                "VALUES (%s, %s, %s, %s, %s, NOW(), TRUE, NOW()) "
                "ON DUPLICATE KEY UPDATE "
                "TileURL=%s,TileType=%s,TileMSG=%s,MSGID=%s,TurnsNeutral=%s,ForceUpdate=%s,LastUpdate=%s;")
    cursor = db.cursor()
    try:
        cursor.execute(add_tile, (
            tc.id, tc.url, int(tc.type), tc.msg, tc.msg_id, tc.url, int(tc.type), tc.msg, tc.msg_id,
            tc.refreshTimer,
            tc.shouldUpdate, tc.lastUpdate))
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        db.rollback()
        return

    db.commit()
    cursor.close()


async def deleteTile(db, tilecode):
    remove_tile = "DELETE FROM Tile WHERE TileCode='%s'"
    cursor = db.cursor()
    cursor.execute(remove_tile, tilecode)
    db.commit()
    cursor.close()


async def updateTileList(db, tcList):
    add_tile = ("INSERT INTO Tile (TileCode, TileURL, TileType, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate) "
                "VALUES (%s, %s, %s, %s, %s, NOW(), FALSE, NOW()) "
                "ON DUPLICATE KEY UPDATE "
                "TileURL=%s, TileType=%s, TileMSG=%s, MSGID=%s, TurnsNeutral=%s, ForceUpdate=%s, LastUpdate=%s;")

    cursor = db.cursor()
    for tc in tcList:
        cursor.execute(add_tile, (tc.id, tc.url, int(tc.type), tc.msg, tc.msg_id, tc.url, int(tc.type), tc.msg, tc.msg_id, tc.refreshTimer, tc.shouldUpdate, tc.lastUpdate))
    db.commit()
    cursor.close()


async def getAllTiles(db, channel):
    c = db.cursor()
    c.execute("SELECT * FROM Tile;")
    TileList = []
    for (TileCode, TileURL, tt, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate) in c:
        if MSGID is None:
            MSGID = 0
        TileList.append(TileClass(db, TileCode, TileURL, tt, TileMSG, int(MSGID), TurnsNeutral, ForceUpdate, LastUpdate, channel))
    c.close()
    return TileList


async def findByTileCode(db, tilecode):
    c = db.cursor()
    c.execute("SELECT * FROM Tile WHERE TileCode = '%s LIMIT 1;", (tilecode,))
    ret = c.fetchone()
    for (TileCode, TileURL, tt, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate) in c:
        return TileClass(db, TileCode, TileURL, tt, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate)
    c.close()
    return None


async def findByMSGID(db, msg_id):
    c = db.cursor()
    c.execute("SELECT * FROM Tile WHERE MSGID = %s LIMIT 1;", (msg_id,))
    ret = c.fetchone()
    for (TileCode, TileURL, tt, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate) in c:
        return TileClass(db, TileCode, TileURL, tt, TileMSG, MSGID, TurnsNeutral, ForceUpdate, LastUpdate)
    c.close()
    return None
