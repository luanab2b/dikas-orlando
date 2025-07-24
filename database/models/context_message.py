from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base
import datetime

class ContextMessage(Base):
    __tablename__ = "context_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    context_id = Column(Integer, ForeignKey("conversation_contexts.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    function_call_id = Column(String, nullable=True)
    sequence = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    
    # Relacionamentos
    context = relationship("ConversationContext", back_populates="messages")
    
    def to_dict(self):
        return {
            "id": self.id,
            "context_id": self.context_id,
            "role": self.role,
            "content": self.content,
            "function_call_id": self.function_call_id,
            "sequence": self.sequence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }