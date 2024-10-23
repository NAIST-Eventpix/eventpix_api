from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from src.eventpix_api.lib import pick_schedule_from_image

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/pick_schedule_from_image")
async def api_pick_schedule_from_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return JSONResponse(content=pick_schedule_from_image(contents))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
