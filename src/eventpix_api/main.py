import json

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from eventpix_api.lib import (
    json_to_ics,
    pick_schedule_from_image,
    pick_schedule_from_text,
)

app = FastAPI()


class TextInput(BaseModel):
    text: str


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.post("/pick_schedule_from_image")
async def api_pick_schedule_from_image(file: UploadFile = File(...)) -> JSONResponse:
    try:
        contents = await file.read()
        return JSONResponse(content=pick_schedule_from_image(contents))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/pick_schedule_from_text")
async def api_pick_schedule_from_text(input: TextInput) -> JSONResponse:
    try:
        text = input.text
        schedule = pick_schedule_from_text(text)
        return JSONResponse(content=schedule)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/convert_json_to_ics")
async def convert_json_to_ics(file: UploadFile = File(...)) -> Response:
    try:
        contents = await file.read()
        json_data = json.loads(contents)
        events = json_data.get("events", [])
        ics_content = json_to_ics(events)
        return Response(
            content=ics_content,
            media_type="text/calendar",
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
