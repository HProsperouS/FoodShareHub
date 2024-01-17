from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base
from utils.helper import get_current_time_in_singapore

class ChatFile(Base):
    __tablename__ = "ChatFiles"

    Id = Column(Integer, primary_key=True, index=True)
    FileName = Column(String, default="")
    ContentType = Column(String, default="")
    FileSize = Column(Integer, default="")
    FilePath = Column(String, default="")
    PublicAccessURL = Column(String, default="")

    MessageId = Column(Integer, ForeignKey('Messages.Id'), nullable=False)
    Message = relationship("Message", back_populates="ChatFiles")

class Message(Base):
    __tablename__ = 'Messages'
    Id = Column(Integer, primary_key=True)
    Sender = Column(String, nullable=False)
    Receiver = Column(String, nullable=False)
    Content = Column(String(1000), nullable=False)
    Type = Column(String, nullable=False)
    SendTime = Column(DateTime, default=get_current_time_in_singapore)
    IsRead = Column(Boolean, default=False)

    ConversationId = Column(Integer, ForeignKey('Conversations.Id'), nullable=False)
    ChatFiles = relationship("ChatFile", back_populates="Message")

    def __repr__(self):
        return f"Message(Id={self.Id}, Sender='{self.Sender}', Receiver='{self.Receiver}', Content='{self.Content}', Type='{self.Type}', SendTime='{self.SendTime}', IsRead={self.IsRead}, ConversationId={self.ConversationId})"
    
class Conversation(Base):
    __tablename__ = 'Conversations'
    Id = Column(Integer, primary_key=True)
    Participant1 = Column(String, nullable=False)
    Participant2 = Column(String, nullable=False)
    LastMessageId = Column(Integer, nullable=True)
    StartTime = Column(DateTime, default=get_current_time_in_singapore)
    LastMessageTime = Column(DateTime, nullable=True)
    
    Messages = relationship("Message", backref="conversation")

