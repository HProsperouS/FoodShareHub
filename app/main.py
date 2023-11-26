# Import third-party libraries
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from fastapi.responses import (
    FileResponse, 
    ORJSONResponse
)
from starlette.routing import Mount

# Import local libraries
import utils.constants as C
import routers

# import Python's standard libraries

templates = Jinja2Templates(directory="templates")

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
    swagger_ui_oauth2_redirect_url=None
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    flash_message_text = "This is a custom flash message!"
    flash_message_class = "alert-success"  
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "flash_message_text": flash_message_text, "flash_message_class": flash_message_class}
    )


"""--------------------------- Start of App Routes ---------------------------"""
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # TODO: Edit your favicon.ico in the static folder
    return FileResponse(C.FAVICON_PATH)

# Web routers
app.include_router(routers.foodsharerouter)

"""--------------------------- End of App Routes ---------------------------"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="localhost", 
        port=8080,
        reload=True,
        log_level="debug",
    )
