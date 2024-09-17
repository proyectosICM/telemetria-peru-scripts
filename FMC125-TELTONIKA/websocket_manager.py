import json
import websockets
import asyncio

async def send_to_websocket(data, uri="ws://localhost:6061"):
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps(data))
        print(f"Datos enviados al WebSocket: {json.dumps(data, indent=4)}")
