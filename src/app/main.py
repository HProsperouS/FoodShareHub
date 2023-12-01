import orjson
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import (
    FileResponse, 
    RedirectResponse,
    HTMLResponse
)

from starlette.staticfiles import StaticFiles
from starlette.routing import Mount
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# import Python's standard libraries

# Import local libraries
import utils.constants as C
from routers import * 
from utils import (
    flash, 
    render_template,
)
from utils.classes import PrettyORJSON
from middleware import add_app_exception_handlers
from db.dependencies import init_db

# Load Environment Variables
load_dotenv()

app = FastAPI(
    title="FoodShareHub",
    debug=C.DEBUG_MODE,
    version="1.0.0",
    routes=[
        Mount(
            path="/static", 
            app=StaticFiles(
                directory=str(C.APP_ROOT_PATH.joinpath("static"))
            ), 
            name="static"
        ),
    ],
    default_response_class=PrettyORJSON,
    docs_url="/docs" if C.DEBUG_MODE else None,
    redoc_url="/redoc" if C.DEBUG_MODE else None,
    openapi_url="/openapi.json" if C.DEBUG_MODE else None,
    swagger_ui_oauth2_redirect_url=None,
)

def add_middlewares(app: FastAPI) -> None:
    """Add middlewares to the FastAPI app.

    Args:
        app (FastAPI):
            The FastAPI app.
    """
    app.add_middleware(
        SessionMiddleware,
        secret_key="change_me",
        session_cookie=C.SESSION_COOKIE,
        https_only=not C.DEBUG_MODE,
    )
    add_app_exception_handlers(app)

"""--------------------------- Start of App Routes ---------------------------"""

# Web routers
def add_routers(app: FastAPI) -> None:
    """Add routers to the FastAPI app.

    Args:
        app (FastAPI):
            The FastAPI app.
    """
    app.include_router(foodshare_router)
    app.include_router(allroles_router)
    app.include_router(guest_router)
    app.include_router(user_router)
    app.include_router(admin_router)

"""--------------------------- End of App Routes ---------------------------"""

# Initialize the database
init_db()
add_middlewares(app)
add_routers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="localhost", 
        port=8080,
        reload=True,
        log_level="debug",
    )
