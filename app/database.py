from pymongo import ASCENDING, MongoClient
from gridfs import GridFSBucket

from app.config import settings

client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_database]

bucket = GridFSBucket(
    db,
    bucket_name=settings.gridfs_bucket,
)

files_collection = db[f"{settings.gridfs_bucket}.files"]

index_name = files_collection.create_index(
    [
        ("metadata.school_id", ASCENDING),
        ("metadata.student_id", ASCENDING),
    ],
    unique=True,
)