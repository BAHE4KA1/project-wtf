from typing import List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        self.active_connections.setdefault(chat_id, []).append(websocket)

    async def disconnect(self, websocket: WebSocket, chat_id: str):
        if chat_id in self.active_connections:
            if websocket in self.active_connections[chat_id]:
                self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, message: dict, chat_id: str):
        connections = self.active_connections.get(chat_id, [])
        for connection in connections[:]:  # Используем копию списка
            try:
                await connection.send_json(message, mode='text')
            except Exception as e:

                print(f"Ошибка при отправке сообщения: {e}")
                await self.disconnect(connection, chat_id)
