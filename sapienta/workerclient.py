import dramatiq
import click
import os
import base64
import minio
import uuid
import hashlib

from dotenv import load_dotenv

from typing import Optional

from sapienta import get_minio_client
from sapienta.worker import convert, split, annotate

@click.command()
@click.argument("in_file", type=click.Path(file_okay=True, exists=True))
def main(in_file: str):
    """Run Sapienta pipeline on IN_FILE, automatically applying operations as needed"""

    load_dotenv()

    mc = get_minio_client()

    pipe: Optional[dramatiq.pipeline] = None

    if in_file.endswith(".pdf"):

        key = f"{uuid.uuid4()}.pdf"
        pipe = (convert.message_with_options(args=[key]) | split.message() | annotate.message())

    elif in_file.endswith(".xml"):
        key = f"{uuid.uuid4()}.xml"
        pipe = (split.message_with_options(args=[key]) | annotate.message())

    else:
        print("Invalid file type")
        return 1

    mc.fput_object(os.environ.get("MINIO_BUCKET"), key, in_file)  

    if pipe is None:
        print("No pipeline - something went wrong")
        return 1

    pipe.run()
    r = pipe.get_result(block=True, timeout=120000)

    print(r)

if __name__ == "__main__":
    main()