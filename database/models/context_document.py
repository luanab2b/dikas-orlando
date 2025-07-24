# database/models/context_document.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from database.config import Base

class ContextDocument(Base):
    __tablename__ = "context_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    context_id = Column(Integer, ForeignKey("conversation_contexts.id"), nullable=False)
    
    # Renomeie metadata para document_metadata ou outra coisa
    document_metadata = Column(Text, nullable=True)  # Renomeado de "metadata" para evitar conflito
    
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now)
    
    # Relacionamento com o contexto da conversa
    context = relationship("ConversationContext", back_populates="documents")
    
    def to_dict(self):
        return {
            "id": self.id,
            "context_id": self.context_id,
            "document_metadata": self.document_metadata,  # Nome corrigido
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }