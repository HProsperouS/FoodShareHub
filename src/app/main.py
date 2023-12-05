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
import routers
from utils import (
    flash, 
    render_template,
)
from utils.classes import PrettyORJSON
from middleware import add_app_exception_handlers
from db.dependencies import init_db

# Load Environment Variables
load_dotenv()
# from models.response import PrettyORJSON
from datetime import datetime, timedelta
# import aioredis

# redis cached endpoint
# redis_pool = aioredis.from_url("testcache-ampw1p.serverless.use1.cache.amazonaws.com:6379")

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
        max_age=600,
        # storage=aioredis.RedisStorage(redis_pool) # stores in redis now
    )
    add_app_exception_handlers(app)

"""--------------------------- Start of App Routes ---------------------------"""




"""--------------------------- Start of App Routes ---------------------------"""

# @app.get("/favicon.ico", include_in_schema=False)
# async def favicon():
#     # TODO: Edit your favicon.ico in the static folder
#     return FileResponse(C.FAVICON_PATH)

# Web routers
def add_routers(app: FastAPI) -> None:
    """Add routers to the FastAPI app.

    Args:
        app (FastAPI):
            The FastAPI app.
    """
    # Web routers
    app.include_router(routers.foodshare_router)
    app.include_router(routers.allroles_router)
    app.include_router(routers.guest_router)
    app.include_router(routers.user_router)
    app.include_router(routers.admin_router)
    app.include_router(routers.authentication_router)
    # API routers
    app.include_router(routers.foodshare_api)



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
