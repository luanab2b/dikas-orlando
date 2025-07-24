# repositories/message_repository.py

from interfaces.repositories.message_repository_interface import IMessageRepository
from interfaces.clients.database_interface import IDatabase
from database.models.message_model import Message
import json

class MessageRepository(IMessageRepository):
    def __init__(self, database_client: IDatabase):
        self.db = database_client

    def all(self) -> list:
        with self.db.get_session() as session:
            messages = session.query(Message).all()
            return [message for message in messages] or []

    def get_latest_customer_messages(
        self, phone: int | None = None, limit: int = 20
    ) -> list:
        with self.db.get_session() as session:
            query = (
                session.query(Message)
                .filter_by(phone=phone)
                .order_by(Message.id.desc())
            )

            if limit:
                query = query.limit(limit)

            messages = query.all()

            return [message.to_dict() for message in messages] or []

    def create(self, phone: str, role: str, content: str | list) -> dict:
        with self.db.get_session() as session:
            message = Message(
                phone=phone,
                role=role,
                content=content if isinstance(content, str) else json.dumps(content),
            )
            session.add(message)
            return message.to_dict()