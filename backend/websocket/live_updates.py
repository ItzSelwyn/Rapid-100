from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("Dashboard connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print("Dashboard disconnected")

    async def broadcast(self, message: dict):
        dead = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                dead.append(connection)

        # remove broken sockets (CRITICAL)
        for d in dead:
            self.disconnect(d)

manager = ConnectionManager()
