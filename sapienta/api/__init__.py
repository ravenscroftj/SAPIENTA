import uuid
import os
import minio


from fastapi import FastAPI, File, UploadFile, HTTPException, Response, WebSocket
from sapienta import get_minio_client
from sapienta.worker import convert, split, annotate
from pydantic import BaseModel
from typing import Optional

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))

@app.get("/")
def get_index_html():
    with open(os.environ.get("SAPIENTA_INDEX_FILE","static/index.html")) as f:
        return HTMLResponse( f.read())

class JobResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    conversion_complete: bool
    split_complete: bool
    annotation_complete: bool
    error: Optional[str]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

@app.get("/{job_id}/result")
def get_result(job_id: str):

    mc = get_minio_client()

    obj = None

    try:
        obj = mc.get_object(os.environ.get("MINIO_BUCKET"), f"{job_id}_annotated.xml")

        return Response(content=obj.read(), media_type="application/xml")
    except minio.error.S3Error as e:
        if e._code == "NoSuchKey":
            return HTTPException(status_code=404, detail="Job not yet complete, check with status endpoint")
    except:
        return HTTPException(status_code=500, detail="Something went wrong, that's all we know...")
    #     results[prop] = False
    finally:
        if obj is not None:
            obj.close()

    



@app.post("/{job_id}/status", response_model=JobStatusResponse, response_model_exclude_unset=True)
def check(job_id: str) -> JobStatusResponse:
    """Check status of running annotation job"""

    mc = get_minio_client()


    objects = list(mc.list_objects(os.environ.get("MINIO_BUCKET"), job_id))

    # is this even a job we know about?
    if len(objects) < 1:
        raise HTTPException(status_code=404, detail="No job found with that ID. Try a valid ID.")

    job_steps = {
        f"{job_id}.xml":"conversion_complete",
        f"{job_id}_split.xml": "split_complete",
        f"{job_id}_annotated.xml": "annotation_complete"
    }

    results = {step: False for step in job_steps.values()}

    for obj in objects:
        if obj.object_name in job_steps:
            results[job_steps[obj.object_name]] = True
        elif obj.object_name == f"{job_id}_error":
            results['error'] = mc.get_object(os.environ.get("MINIO_BUCKET"), obj.object_name).read()

    return JobStatusResponse(**results)
            



@app.post("/submit")
def process(file: UploadFile = File(...)) -> JobResponse:
    
    mc = get_minio_client()
    job_id = uuid.uuid4()
    
    if file.filename.endswith(".pdf"):
        
        key = f"{job_id}.pdf"
        pipe = (convert.message_with_options(args=[key]) | split.message() | annotate.message())

    elif file.filename.endswith(".xml"):
        key = f"{job_id}.xml"
        pipe = (split.message_with_options(args=[key]) | annotate.message())

    else:
        raise HTTPException(status_code=400, detail="Invalid file type upload")

    content = file.file.read()
    file.file.seek(0)

    mc.put_object(os.environ.get("MINIO_BUCKET"), key, file.file, len(content), file.content_type)  

    pipe.run()

    return JobResponse(job_id=str(job_id))

