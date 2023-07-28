import os.path

import fastapi
import fastapi.staticfiles

try:
    from room import Room
except ImportError:
    from .room import Room

app = fastapi.FastAPI(
    title="Timebomb Backend",
    summary="Timebomb backend",
    description="Timebomb's backend for interacting with stuffs",
)

current_dir = os.getcwd()

rooms: dict[int, Room] = {}

app.mount("/", fastapi.staticfiles.StaticFiles(directory=current_dir + "/front-end"))


@app.websocket("/backend/ws")
async def websocket(ws: fastapi.WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_json()
            if msg["state"] == "join":
                if msg["room"] in rooms.keys():
                    await rooms[msg["room"]].join(ws)
                    break
                else:
                    await ws.send_json({"state": "error", "reason": "notfound"})
                    await ws.close()
            elif msg["state"] == "create":
                rooms[msg["id"]] = Room(msg["id"])
                await rooms[msg["id"]].join(ws)
                await rooms[msg["id"]].task  # pinger
    except fastapi.WebSocketDisconnect:
        for room in rooms.values():
            await room.check_disconnected()
