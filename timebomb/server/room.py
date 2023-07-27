import asyncio
import enum
import json

import async_timeout
import fastapi
import fastapi.websockets


class RoomState(enum.Enum):
    Idle = 0
    Running = 1


class Left(Exception):
    pass


class Player:
    def __init__(self, ws: fastapi.websockets.WebSocket):
        self.name = ""
        self.hearts = 0
        self.ws = ws

    async def get_info(self, ws: fastapi.WebSocket) -> None:
        await self.ws.send_json({"state": "requested_informations"})
        try:
            infos = await self.ws.receive_json()
            self.name = infos["name"]
        except (KeyError, fastapi.WebSocketDisconnect):
            await self.ws.close()
            raise Left()

    async def send(self, content: str):
        await self.ws.send(content)


class Game:
    def __init__(self, room: "Room") -> None:
        self.room = room


class Chat:
    def __init__(self, room: "Room") -> None:
        self.room = room


class Room:
    def __init__(self) -> None:
        self.players: list[Player] = []
        self.limit = 10  # limit players
        self.state = RoomState.Idle
        self.game = Game(self)
        self.chat = Chat(self)
        self.threadings: dict[Player, asyncio.Task] = []
        self.pinger_enabled = False

    async def broadcast_all(self, data: str):
        for player in self.players:
            await player.send(data)

    async def listen(self, player: Player):
        failed = 0
        while True:
            try:
                a = await player.ws.receive_json()
            except:
                await self.check_disconnected()
                failed += 1
            if failed >= 5:
                break
            if a["state"] == "request_players":
                await player.ws.send_json(
                    [{"name": x.name, "hearts": x.hearts} for x in self.players]
                )
            elif a["state"] == "send_message":
                await self.chat.send_all(a["content"])
            elif a["state"] == "request_messages":
                await player.ws.send_json(await self.chat.get_chat())
        await player.ws.close(reason="too many fails")

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
                        assert (json.loads(await player.recieve()))[
                            "state"
                        ] == "pong", "Not ponged"
                except AssertionError:
                    await player.disconnect()
                    raise fastapi.WebSocketDisconnect()
            except fastapi.WebSocketDisconnect:
                await player.disconnect()
                self.players.remove(player)

    async def join(self, ws: fastapi.websockets.WebSocket) -> None:
        if not self.pinger_enabled:
            a = asyncio.create_task(self.pinger())

        if len(self.players) >= 10:
            await ws.send_json({"state": "error", "reason": "full"})
        p = Player()
        await p.get_info(ws)
        self.players.append(p)
        self.threadings[p] = asyncio.create_task(self.listen(p))
        await ws.send_json({"state": "success"})
    
    async def cleanup(self):
        for task in self.threadings.values():
            task.cancel()
        for player in self.players:
            await player.ws.close(reason="shutdown")