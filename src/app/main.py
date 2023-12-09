# import third-party libraries
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.routing import Mount
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

# Import local libraries
import utils.constants as C
import routers
from utils.classes import PrettyORJSON
from middleware import add_app_exception_handlers
from db.dependencies import init_db

# import aioredis

# redis cached endpoint
# redis_pool = aioredis.from_url("testcache-ampw1p.serverless.use1.cache.amazonaws.com:6379")

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
        max_age=600,
        # storage=aioredis.RedisStorage(redis_pool) # stores in redis now
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
