from click.decorators import command
from sapienta import get_minio_client
from datetime import datetime, timedelta, timezone
from minio.deleteobjects import DeleteObject
import click
import os
import dotenv
import logging

dotenv.load_dotenv()


@click.command()
@click.option("--threshold", "-t", type=int, help="number of hours to delete before", default=24)
@click.option("--quiet","-q", type=bool, is_flag=True, default=False)
def main(threshold, quiet):

    logger = logging.getLogger("sapienta.worker.cleanup")

    if not quiet:
        logging.basicConfig(level=logging.INFO)

    mc = get_minio_client()
    objects = mc.list_objects(os.getenv("MINIO_BUCKET"))

    threshold = (datetime.utcnow() - timedelta(hours=threshold)).replace(tzinfo=timezone.utc)

    logger.info(f"Looking for objects older than {threshold}")

    rmbatch = []
    for obj in objects:
        if obj.last_modified < threshold:
            rmbatch.append(DeleteObject(obj.object_name))

        if len(rmbatch) > 100:
            logger.info(f"Removing batch of {len(rmbatch)} objects")
            for err in mc.remove_objects(os.getenv("MINIO_BUCKET"), rmbatch):
                logger.error(err)
            rmbatch = []

    if len(rmbatch) > 0:
        logger.info(f"Removing batch of {len(rmbatch)} objects")
        for err in mc.remove_objects(os.getenv("MINIO_BUCKET"), rmbatch):
            logger.error(err)


if __name__ == "__main__":
    main()
