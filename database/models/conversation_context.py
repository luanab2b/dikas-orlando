from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base
import datetime

class ConversationContext(Base):
    __tablename__ = "conversation_contexts"
    
    ID = Column(Integer, primary_key=True, index=True)
    USER_ID = Column(Integer, ForeignKey("users.id"), nullable=False)
    SESSION_ID = Column(String, nullable=False)
    AGENT_ID = Column(String, nullable=False)
    CREATED_AT = Column(DateTime(timezone=True), default=datetime.datetime.now) 
    
    #relationships
    user = relationship("User", back_populates="contexts")
    messages = relationship("ContextMessage", back_populates="context", cascade="all, delete-orphan")
    documents = relationship("ContextDocument", back_populates="context", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.ID,
            "user_id": self.USER_ID,
            "session_id": self.SESSION_ID,
            "agent_id": self.AGENT_ID,
            "created_at": self.CREATED_AT.isoformat() if self.CREATED_AT else None,
            "messages": [message.to_dict() for message in self.messages],
            "documents": [document.to_dict() for document in self.documents],
        }