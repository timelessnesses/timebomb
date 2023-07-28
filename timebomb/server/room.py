import asyncio
import enum
import json

import async_timeout
import fastapi
import fastapi.websockets
import logging


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
        self.logger = logging.getLogger(f"timebomb.server.room.Player[{self.name}]")

    async def get_info(self, ws: fastapi.WebSocket) -> None:
        await self.ws.send_json({"state": "requested_informations"})
        try:
            self.logger.info("Fetching player's information.")
            infos = await self.ws.receive_json()
            self.logger.info("Got Information.")
            self.name = infos["name"]
            self.logger = logging.getLogger(f"timebomb.server.room.Player[{self.name}]")
            self.logger.info("Updated.")
        except (KeyError, fastapi.WebSocketDisconnect) as e:
            self.logger.error(f"{'Invalid Response from player.' if isinstance(e, KeyError) else 'Player disconnected.'} Closing Connection.")
            await self.ws.close()
            raise Left()

    async def send(self, content: str):
        self.logger.info(f"Broadcasting content: {content}")
        await self.ws.send(content)
        self.logger.info("Sent.")
    
    def __str__(self) -> str:
        return self.name

class Game:
    def __init__(self, room: "Room") -> None:
        self.room = room


class Chat:
    def __init__(self, room: "Room") -> None:
        self.room = room


class Room:
    def __init__(self, id: str) -> None:
        self.id = id
        self.logger = logging.getLogger(f"timebomb.server.room.Room({id})")
        self.players: list[Player] = []
        self.limit = 10  # limit players
        self.state = RoomState.Idle
        self.logger.info("Initializing Game.")
        self.game = Game(self)
        self.logger.info("Initialized Game.")
        self.logger.info("Initializing Chat.")
        self.chat = Chat(self)
        self.logger.info("Initialized Chat.")
        self.threadings: dict[Player, asyncio.Task] = []
        self.logger.info("Running pinger task in the background.")
        self.pinger_task = asyncio.create_task(self.pinger())
        self.logger.info("Ran pinger task in the background.")
        self.logger.info("Initialized Room.")

    async def broadcast_all(self, data: str):
        self.logger.info("Broadcast all is called.")
        for player in self.players:
            self.logger.info(f"Broadcasting to {player}")
            await player.send(data)

    async def listen(self, player: Player):
        logger = logging.getLogger(f"timebomb.server.room.Room({self.id}).listen({player})")
        logger.info(f"Listening to {player} request.")
        failed = 0
        while True:
            self.logger.info("Listening...")
            try:
                a = await player.ws.receive_json()
                logger.info(f"Got request: {a}")
            except:
                logger.error("Error while listening for JSON. (Could be either malformed JSON request body or disconnected.)")
                self.logger.info("Checking Disconnected players.")
                await self.check_disconnected()
                failed += 1
                logger.info(f"Increased failed count. ({failed})")
            if failed >= 5:
                logger.info("Failed request body more than 5 times. Disconnecting from player.")
                break
            if a["state"] == "request_players":
                logger.info("Requested players informations.")
                await player.ws.send_json(
                    [{"name": x.name, "hearts": x.hearts} for x in self.players]
                )
            elif a["state"] == "send_message":
                logger.info("Send message.")
                await self.chat.send_all(a["content"])
            elif a["state"] == "request_messages":
                logger.info("Request message history.")
                await player.ws.send_json(await self.chat.get_chat())
        await player.ws.close(reason="too many fails")

    async def pinger(self) -> None:
        logger = logging.getLogger(f"timebomb.server.room.Room({self.id}).pinger")
        logger.info("Initialized.")
        while True:
            logger.info("Pinging.")
            await self.check_disconnected()
            logger.info("Done pinging. Sleeping for 3 seconds.")
            await asyncio.sleep(3)

    async def check_disconnected(self) -> None:
        logger = logging.getLogger(f"timebomb.server.room.Room({self.id}).check_disconnected")
        logger.info("Check disconnection called.")
        for player in self.players:
            logger.info(f"Pinging {player}")
            try:
                logging.info("Sending ping.")
                await player.send(json.dumps({"state": "ping"}))
                logging.info("Sent ping.")
                try:
                    async with async_timeout.timeout(5):
                        logging.info("Waiting for pong. (5 seconds.)")
                        assert (json.loads(await player.recieve()))[
                            "state"
                        ] == "pong", "Not ponged"
                        logging.info("Got pong.")
                except (AssertionError, asyncio.exceptions.TimeoutError) as e:
                    logging.info(f"{'Invalid Response.' if isinstance(e,AssertionError) else 'Timed out.'} Disconnecting.")
                    raise fastapi.WebSocketDisconnect()
            except fastapi.WebSocketDisconnect:
                await player.disconnect()
                self.players.remove(player)
                logging.info(f"Removed {player} (No ping.)")

    async def join(self, ws: fastapi.websockets.WebSocket) -> None:

        if len(self.players) >= 10:
            await ws.send_json({"state": "error", "reason": "full"})
            return
        p = Player()
        await p.get_info(ws)
        self.players.append(p)
        self.threadings[p] = asyncio.create_task(self.listen(p))
        await ws.send_json({"state": "success"})
    
    async def cleanup(self):
        for task in self.threadings.values():
            task.cancel()
        self.pinger_task.cancel()
        for player in self.players:
            await player.ws.close(reason="shutdown")
        
    def __del__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.cleanup())