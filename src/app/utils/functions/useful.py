# import third-party libraries
# import bson
# import httpx
# import orjson
# import ipinfo
# import aiofiles
# import aiofiles.os as aiofiles_os
# from pydantic import BaseModel, HttpUrl
# from pydantic.error_wrappers import ValidationError
from fastapi import Request, FastAPI, WebSocket
# from fastapi.exceptions import HTTPException

# import local Python libraries
from utils import constants as C

# import Python's standard libraries
# import html
# import time
# import base64
# import pathlib
# import asyncio
# import hashlib
# import logging
# from typing import Any
# from zoneinfo import ZoneInfo
# from datetime import datetime

def flash(request: Request, message: str, category: str = "primary") -> None:
    """Adds a message to the session.

    Note: Use the get_flashed_messages function in Jinja2 to retrieve the messages.

    Args:
        request (Request):
            The request object.
        message (str):
            The message to add
        category (str):
            The category of the message

    Returns:
        None
    """
    flash_message = {"message": message, "category": category}
    if C.FLASH_MESSAGES not in request.session:
        request.session[C.FLASH_MESSAGES] = []
    request.session[C.FLASH_MESSAGES].append(flash_message)