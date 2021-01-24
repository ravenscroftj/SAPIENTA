import dramatiq
import tempfile
import os
import requests

from sapienta.tools.converter import PDFXConverter
from sapienta.tools.annotate import Annotator
from sapienta.tools.sssplit import SSSplit as Splitter

from dramatiq.rate_limits import ConcurrentRateLimiter
from dramatiq.rate_limits.backends import RedisBackend

from sapienta import get_minio_client

backend = RedisBackend(host=os.environ.get("REDIS_HOST", 'localhost'), 
    password=os.environ.get("REDIS_PASSWORD", None))

PDFX_MUTEX = ConcurrentRateLimiter(backend, "distributed-mutex", limit=2)



def report_success(job_id, step):
    """Report that a particular step has been completed"""

    #try:
    requests.post(f"{os.environ['SAPIENTA_ENDPOINT']}/{job_id}/progress",
                      params={'challenge': os.environ['SAPIENTA_WORKER_PASSWORD']},
                      json={"status": "complete", "step": step}
                      )

    #except Exception as e:
    #    print(f"I failed to log job progress for {job_id} because {e} :(")


@dramatiq.actor(store_results=True, max_retries=3)
def convert(pdf_key: str) -> str:
    """Convert a PDF to an XML"""

    with PDFX_MUTEX.acquire():

        logger = dramatiq.get_logger(__name__)

        conv = PDFXConverter()

        mc = get_minio_client()

        nameroot, _ = os.path.splitext(pdf_key)
        out_key = f"{nameroot}.xml"

        with tempfile.TemporaryDirectory() as tmpdir:

            in_pdf = os.path.join(tmpdir, "in.pdf")
            out_xml = os.path.join(tmpdir, "out.xml")

            logger.info("Fetch PDF from S3 storage")

            mc.fget_object(os.environ.get("MINIO_BUCKET"), pdf_key, in_pdf)

            logger.info("Run PDF conversion process")
            conv.convert(in_pdf, out_xml)

            mc.fput_object(os.environ.get("MINIO_BUCKET"), out_key, out_xml)

            logger.info("Store result XML in S3 storage")

            report_success(nameroot, "convert_pdf")

        return out_key


@dramatiq.actor(store_results=True, max_retries=3)
def split(xml_key: str) -> str:
    """Split an xml into sentences"""

    logger = dramatiq.get_logger(__name__)

    splitter = Splitter()

    mc = get_minio_client()

    nameroot, _ = os.path.splitext(xml_key)

    out_key = f"{nameroot}_split.xml"

    with tempfile.TemporaryDirectory() as tmpdir:
        in_xml = os.path.join(tmpdir, "in.xml")
        out_xml = os.path.join(tmpdir, "out.xml")

        logger.info("Fetch XML doc from S3 storage")

        mc.fget_object(os.environ.get("MINIO_BUCKET"), xml_key, in_xml)

        logger.info("Running sentence split")
        splitter.split(in_xml, out_xml)

        logger.info("Save XML doc to S3 storage")

        mc.fput_object(os.environ.get("MINIO_BUCKET"), out_key, out_xml)

        report_success(nameroot, "split")

    return out_key


@dramatiq.actor(store_results=True)
def annotate(xml_key: str) -> str:
    """Annotate split xml file"""

    logger = dramatiq.get_logger(__name__)

    anno = Annotator()

    mc = get_minio_client()

    nameroot = os.path.splitext(xml_key)[0].split("_")[0]

    out_key = f"{nameroot}_annotated.xml"

    with tempfile.TemporaryDirectory() as tmpdir:
        in_xml = os.path.join(tmpdir, "in.xml")
        out_xml = os.path.join(tmpdir, "out.xml")

        logger.info("Fetch XML doc from S3 storage")

        mc.fget_object(os.environ.get("MINIO_BUCKET"), xml_key, in_xml)

        logger.info("Running sentence split")
        anno.annotate(in_xml, out_xml)

        logger.info("Save XML doc to S3 storage")

        mc.fput_object(os.environ.get("MINIO_BUCKET"), out_key, out_xml)

        report_success(nameroot, "annotate")

    return out_key
