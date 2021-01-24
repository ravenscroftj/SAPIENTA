from typing import List, Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.subscriptions: Dict[str, List[WebSocket]] = {}

    def disconnect(self, websocket: WebSocket):

        to_del = set()

        for job_id in self.subscriptions:
            if websocket in self.subscriptions[job_id]:
                self.subscriptions[job_id].remove(websocket)

                if len(self.subscriptions[job_id]) < 1:
                    to_del.add(job_id)

        for job_id in to_del:
            del self.subscriptions[job_id]

    def subscribe(self, job_id: str, websocket: WebSocket):
        if job_id not in self.subscriptions:
            self.subscriptions[job_id] = []

        self.subscriptions[job_id].append(websocket)

    async def broadcast(self, job_id: str, message: str):
        """Broadcast a status update for subscriptions to a particular job"""
        for connection in self.subscriptions[job_id]:
            await connection.send_text(message)


manager = ConnectionManager()
