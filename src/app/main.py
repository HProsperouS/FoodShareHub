import orjson
from fastapi import FastAPI
from fastapi.responses import (
    FileResponse, 
    ORJSONResponse,
    RedirectResponse,
    HTMLResponse
)
from starlette.staticfiles import StaticFiles
from starlette.routing import Mount
from starlette.middleware.sessions import SessionMiddleware
# import Python's standard libraries

# Import local libraries
import app.utils.constants as C
from routers.web import * 

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
    default_response_class=ORJSONResponse,
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
    )

"""--------------------------- Start of App Routes ---------------------------"""
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # TODO: Edit your favicon.ico in the static folder
    return FileResponse(C.FAVICON_PATH)

# Web routers
def add_routers(app: FastAPI) -> None:
    """Add routers to the FastAPI app.

    Args:
        app (FastAPI):
            The FastAPI app.
    """
    app.include_router(foodshare_router)
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
