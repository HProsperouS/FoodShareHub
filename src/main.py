# import third-party libraries
import orjson
from fastapi import FastAPI
from fastapi.responses import (
    FileResponse, 
    ORJSONResponse
)
from fastapi.staticfiles import StaticFiles
from starlette.routing import Mount
from starlette.middleware.sessions import SessionMiddleware

# import Python's standard libraries

# import local libraries
import utils.constants as C
from routers.web import *

app = FastAPI(
    title="Mirai",
    debug=C.DEBUG_MODE,
    version="1.0.0",
    routes=[
        Mount(
            path="/static", 
            app=StaticFiles(
                directory=str(C.STATIC_PATH)
            ), 
            name="static"
        ),
    ],
    default_response_class=ORJSONResponse,
    docs_url="/docs" if C.DEBUG_MODE else None,
    redoc_url="/redoc" if C.DEBUG_MODE else None,
    openapi_url="/openapi.json" if C.DEBUG_MODE else None,
    swagger_ui_oauth2_redirect_url=None,
)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # TODO: Edit your favicon.ico in the static folder
    return FileResponse(C.FAVICON_PATH)

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
    )

def add_routers(app: FastAPI) -> None:
    """Add routers to the FastAPI app.

    Args:
        app (FastAPI):
            The FastAPI app.
    """
    app.include_router(general_router)

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
