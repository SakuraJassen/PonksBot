import datetime


class TileClass:
    def __init__(self, ident, refresh: datetime.datetime):
        self.id = ident
        self.refreshTimer = refresh
        self.message = 0

def init():
    global tileList
    tileList = []
