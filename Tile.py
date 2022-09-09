import datetime
import re
from enum import Flag, auto

class TileType(Flag):
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
        if flag.name is not None:
            if flag != TileType.EMPTY:
                s = flag.name.lower()
        else:
            for f in list(TileType):
                if (f & flag) > 0:
                    s += f"{f.name.lower()}, "
        return s

class TileClass:
    def __init__(self, ident, tileType: TileType, refresh: datetime.datetime):
        self.id = ident
        self.msg = ""
        self.type = tileType
        self.refreshTimer = refresh
        self.msgid = 0
        self.shouldUpdate = False
        self.lastUpdate = datetime.datetime.now()

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
    if ts.total_seconds() > 0:
        expIn = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        return f"{tileProps} Tile: {t.id} | Expires in: {expIn}"
    else:
        return f"{tileProps} Tile: {t.id} | Expired"

async def findByMSGID(msg_id):
    for t in TileList:
        if t.message.id == msg_id:
            return t

def init():
    global TileList
    TileList = []
