import fastapi
import json
import async_timeout
import asyncio
import enum

class RoomState(enum.Enum):
    Idle = 0
    Running = 1

class Left(Exception):
    pass

class Player:
    def __init__(self):
        self.name = ""
        self.hearts = 0

    async def get_info(self, ws: fastapi.WebSocket) -> None:
        await ws.send_json({"state": "requested_informations"})
        try:
            infos = await ws.receive_json()
            self.name = infos["name"]
        except (KeyError, fastapi.WebSocketDisconnect):
            raise Left()

class Room:

    def __init__(self) -> None:
        self.chats: list[dict[str,str]] = []
        self.players: list[Player] = []
        self.limit = 10 # limti players
        self.state = RoomState.Idle
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.pinger())

    async def broadcast_all(self, data: str):
        for player in self.players:
            await player.send(data)

    async def pinger(self) -> None:
        while True:
            await self.check_disconnected()
            await asyncio.sleep(3)

    async def check_disconnected(self) -> None:
        for player in self.players:
            try:
                await player.send(json.dumps({"state": "ping"}))
                try:
                    async with async_timeout.timeout(5):
                        assert (json.loads(await player.recieve()))["state"] == "pong", "Not ponged"
                except AssertionError:
                    raise fastapi.WebSocketDisconnect()
            except fastapi.WebSocketDisconnect:
                await player.disconnect()
                self.players.remove(player)
    
