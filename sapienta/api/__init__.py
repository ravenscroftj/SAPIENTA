import uuid
import os
import minio

from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from sapienta import get_minio_client
from sapienta.worker import convert, split, annotate
from pydantic import BaseModel

app = FastAPI()

class JobResponse(BaseModel):
    job_id: str

class JobStatusResponse(BaseModel):
    conversion_complete: bool
    split_complete: str
    annotation_complete: str

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

    



@app.post("/{job_id}/status")
def check(job_id: str) -> JobStatusResponse:
    """Check status of running annotation job"""

    mc = get_minio_client()

    pairs = [
        (f"{job_id}.xml","conversion_complete"),
        (f"{job_id}_split.xml", "split_complete"),
        (f"{job_id}_annotated.xml", "annotation_complete")
    ]

    results = {}

    for key, prop in pairs: 

        try:
            obj = mc.stat_object(os.environ.get("MINIO_BUCKET"), key)
            results[prop] = True
        except:
            results[prop] = False

    return results
            



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

    return JobResponse(job_id=key)

