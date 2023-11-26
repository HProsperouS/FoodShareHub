from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from fastapi.responses import (
    FileResponse, 
    ORJSONResponse
)
# import local libraries
import utils.constants as C

app = FastAPI()

templates = Jinja2Templates(directory="templates")

static_folder = "static" 
static_app = StaticFiles(directory=static_folder)
app.mount("/static", static_app, name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {
        "page": "Home page"
    }
    flash_message_text = "This is a custom flash message!"
    flash_message_class = "alert-success"  
    # return templates.TemplateResponse("index.html", {"request": request, "data": data, "flash_message_text": flash_message_text, "flash_message_class": flash_message_class})
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "flash_message_text": flash_message_text, "flash_message_class": flash_message_class}
    )
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    # TODO: Edit your favicon.ico in the static folder
    return FileResponse(C.FAVICON_PATH)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="localhost", 
        port=8080,
        reload=True,
        log_level="debug",
    )
