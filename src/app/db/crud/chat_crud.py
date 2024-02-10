from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.chat import Conversation, Message
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from db.models.chat import Conversation, Message
from typing import List
from sqlalchemy.exc import SQLAlchemyError

# Get Unread Messages Sender name
async def get_sendername_of_unread_messages(db: Session, username:str):
    # Username is unique in cognito, so it works as user_id
    result = db.query(Message.Sender).filter(and_(
        Message.Receiver == username,
        Message.IsRead == False
    )).distinct().all()

    return result

async def get_latest_messages_for_user(db: Session, username: str):
    # First, find out all the conversations the user participated in
    conversation_ids = select(Conversation.Id).filter(
        or_(Conversation.Participant1 == username, Conversation.Participant2 == username)
    ).subquery()

    # Then, for each conversation, check if the LastMessageId is null or not
    subquery = select(
        Conversation.Id.label('conversation_id'),
        Conversation.LastMessageId,
    ).where(
        Conversation.Id.in_(conversation_ids)
    ).subquery()

    # Last, get the details of these latest messages or return empty message details if LastMessageId is null
    latest_messages = []
    for conv_id, last_msg_id in db.query(subquery).all():
        if last_msg_id is not None:
            message = db.query(Message).filter(Message.Id == last_msg_id).first()
            latest_messages.append(message)
        else:            
            empty_message = Message(
                Id=0,
                Sender=username, 
                Receiver="", # Receiver should be the opposite user's Username
                Content="",
                Type="text", 
                SendTime="",  
                IsRead=True, # Default to True
                ConversationId=conv_id
            )

            # Get the participant 2 from the conversation table
            participant2 = db.query(Conversation.Participant2).filter(Conversation.Id == conv_id).scalar()
            empty_message.Receiver = participant2
            latest_messages.append(empty_message)

    return latest_messages

async def get_messages_for_user(db: Session, sender: str, receiver:str, AfterSendTime: Optional[str] = None):
    query = db.query(Message).filter(
        or_(
            and_(Message.Sender == sender, Message.Receiver == receiver),
            and_(Message.Sender == receiver, Message.Receiver == sender)
        )
    )

    if AfterSendTime is not None:
        query = query.filter(Message.SendTime > AfterSendTime)

    messages = query.order_by(Message.SendTime).all()

    return [model_to_dict(message) for message in messages]

async def get_chat_notifications(username: str, db: Session):
    query = db.query(Message.Sender,Message.Content, Message.SendTime).filter(
        and_(
            Message.Receiver == username,
            Message.IsRead == False 
        )
    )

    messages = query.order_by(Message.SendTime).all()
    
    return [model_to_dict(message) for message in messages]


async def get_message_by_id_and_sender(db: Session, message_id: int, sender: str):
    return db.query(Message).filter(and_(
        Message.Id == message_id,
        Message.Sender == sender
    )).first()

async def delete_message_by_id(db: Session, message_id: int):
    deleted_count = db.query(Message).filter(Message.Id == message_id).delete()
    db.commit()
    return deleted_count > 0

async def insert_message(db: Session, message: Message, conversation_id: int) -> int:
    """
    Insert a new message into the database, and update the conversation's LastMessageId and LastMessageTime.
    Return the ID of the inserted message.
    
    Args:
    - db (Session): The database session.
    - message (Message): The message object to insert.
    - conversation_id (int): The ID of the conversation to update.

    Returns:
    - int: The ID of the inserted message.

    Raises:
    - SQLAlchemyError: If there is an issue with database operations.
    """
    try:
        db.add(message)
        db.commit()
        db.refresh(message)

        conversation = db.query(Conversation).filter(Conversation.Id == conversation_id).first()
        if conversation:
            conversation.LastMessageId = message.Id
            conversation.LastMessageTime = message.SendTime
            db.commit()

        return message.Id
    except SQLAlchemyError as e:
        db.rollback()
        raise

async def create_conversation(db: Session, sender: str, receiver:str,):
    # Create a new conversation if it doesn't exist
    conversation = db.query(Conversation).filter(
        or_(
                and_(Conversation.Participant1 == sender, Conversation.Participant2 == receiver),
                and_(Conversation.Participant1 == receiver, Conversation.Participant2 == sender)
            )
    ).first()

    # print("conversation", conversation)
    if conversation is None:
        conversation = Conversation(
            Participant1=sender, 
            Participant2=receiver,
            )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)  

async def get_opposite_users(db: Session, current_user: str):
    # Get the opposite users
    opposite_users = db.query(Conversation).filter(
        or_(
            Conversation.Participant1 == current_user,
            Conversation.Participant2 == current_user
        )
    ).order_by(Conversation.StartTime.asc()).all()

    return opposite_users


def model_to_dict(model_instance):
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}
