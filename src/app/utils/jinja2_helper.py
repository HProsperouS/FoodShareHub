# import third-party libraries
from fastapi import (
    Request, 
    FastAPI, 
    WebSocket,
)
from fastapi.responses import (
    Response,
    HTMLResponse,
)
from jinja2 import pass_context
from datetime import datetime, date

# import local libraries
from .constants import (
    FLASH_MESSAGES,
    DOMAIN,
    APP_ROOT_PATH,
    SESSION_COOKIE,
)
from .classes.templating import Jinja2TemplatesAsync

# import Python's standard libraries
import typing

JINJA2_HANDLER = Jinja2TemplatesAsync(
    directory=str(APP_ROOT_PATH.joinpath("templates")), 
    trim_blocks=True,
    lstrip_blocks=True,
    enable_async=True,
)

# Overwrite the existing url_for global function in Jinja2 env
# As the url_for function by default will only return an absolute URL path
@pass_context
def __url_for(context: dict, name: str, external: bool = False, **path_params: typing.Any) -> str:
    return url_for(context["request"], name, external, **path_params)

@pass_context
def get_flashed_messages(context: dict) -> list[dict]:
    request: Request = context["request"]
    if FLASH_MESSAGES in request.session:
        return request.session.pop(FLASH_MESSAGES)
    return []

# Set functions
JINJA2_HANDLER.env.globals["url_for"] = __url_for
JINJA2_HANDLER.env.globals["get_flashed_messages"] = get_flashed_messages

# Set constants
JINJA2_HANDLER.env.globals["SESSION_COOKIE"] = SESSION_COOKIE

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
    if FLASH_MESSAGES not in request.session:
        request.session[FLASH_MESSAGES] = []
    request.session[FLASH_MESSAGES].append(flash_message)

def url_for(request: Request | WebSocket, name: str, external: bool = False, **path_params: typing.Any) -> str:
    """Returns the URL path for the given endpoint name.

    Args:
        request (Request | WebSocket):
            The request object.
        name (str):
            The endpoint name
        external (bool):
            Whether to return an absolute URL path
        **path_params (Any):
            The path parameters

    Returns:
        str:
            The URL path
    """
    app: FastAPI = request.app
    relative_path = app.url_path_for(name, **path_params)
    if external:
        return DOMAIN + relative_path
    return relative_path

async def render_template(headers: dict[str, str] = None, *args: typing.Any, **kwargs: typing.Any) -> HTMLResponse:
    """Renders the Jinja2 template.
    Note: This function is the same as:
    >>> templates_handler.TemplateResponse(*args, **kwargs)

    FastAPI Jinja2 documentation:
    https://fastapi.tiangolo.com/advanced/templates/

    Args:
        name (str): 
            The file path of the HTML template to render.
        context (dict):
            The context to pass to the template.
            Note: Must include the request object.
        status_code (int):
            The status code to return.
        headers (dict):
            The headers to return.
        media_type (str):
            The media type to return.
        background (BackgroundTask):
            The background task to return.

    Returns:
        HTMLResponse:
            The rendered Jinja2 template
    """
    jinja2_response: Response = await JINJA2_HANDLER.TemplateResponse(*args, **kwargs)
    return jinja2_response

def format_date(value):
    if isinstance(value, date):
        month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_name = month_names[value.month]

        formatted_date = "{:02d} {} {}".format(value.day, month_name, value.year)

        return formatted_date
    else:
        raise ValueError("Input must be a datetime.date object")

# Register the filter function with the template environment
JINJA2_HANDLER.env.filters['format_date'] = format_date

