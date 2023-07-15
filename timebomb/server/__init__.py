import aiohttp.web as web
from datetime import datetime
from datetime import timedelta


class Game:
    """
    Main class for timebomb
    """

    routes: web.RouteTableDef
    games: dict[str, Room]
    started: datetime

    def __init__(self) -> None:
        self.routes = web.RouteTableDef()
        self.games = {}
        self.started = datetime.now()
        
    @routes.get()
    async def index(self,req: web.Request) -> web.Response:
        return web.Response(text=f"Time bomb server has been running for {self.running_for}")
    
    @property
    def running_for(self) -> str:
        est = datetime.now() - self.started
        return self.time_builder(est)
    
    def time_builder(self, time: timedelta) -> str:
        days = time.days
        string = ""
        if days <= 365:
            string += f"{days // 365} {'years' if days // 365 > 1 else 'year'},"
            days -= (days // 365) * 365
        if days <= 30:
            string += f"{days // 30} {'months' if days // 30 > 1 else 'month'},"
            days -= (days // 30) * 30
        string += f"{days} {'days' if days > 1 else 'day'}, {time.}"
        