import io
import numpy as np
from app.database import bucket, files_collection

def save_embedding(
    school_id: str,
    student_id: str,
    academic_year: str,
    embedding: np.ndarray,
) -> None:
    buffer = io.BytesIO()
    np.save(buffer, embedding)
    buffer.seek(0)

    bucket.upload_from_stream(
        f"{school_id}_{student_id}_{academic_year}.npy",
        buffer,
        metadata={
            "school_id": school_id,
            "student_id": student_id,
            "academic_year": academic_year,
        },
    )


def load_embedding(
    school_id: str,
    student_id: str,
    academic_year: str,
) -> np.ndarray:
    file = files_collection.find_one(
        {
            "metadata.school_id": school_id,
            "metadata.student_id": student_id,
            "metadata.academic_year": academic_year,
        }
    )

    if file is None:
        raise FileNotFoundError(
            f"No embedding found for student '{student_id}' "
            f"in school '{school_id}' "
            f"for academic year '{academic_year}'."
        )

    stream = io.BytesIO()

    bucket.download_to_stream(
        file["_id"],
        stream,
    )

    stream.seek(0)

    return np.load(stream, allow_pickle=False)


def delete_embedding(
    school_id: str,
    student_id: str,
    academic_year: str,
) -> None:
    files = files_collection.find(
        {
            "metadata.school_id": school_id,
            "metadata.student_id": student_id,
            "metadata.academic_year": academic_year,
        }
    )

    for file in files:
        bucket.delete(file["_id"])


def load_embeddings(
    school_id: str,
    academic_year: str,
    student_ids: list[str] | None = None,
) -> dict[str, np.ndarray]:
    query = {
        "metadata.school_id": school_id,
        "metadata.academic_year": academic_year,
    }

    if student_ids:
        query["metadata.student_id"] = {
            "$in": student_ids,
        }

    embeddings: dict[str, np.ndarray] = {}

    files = files_collection.find(query)

    for file in files:
        stream = io.BytesIO()

        bucket.download_to_stream(
            file["_id"],
            stream,
        )

        stream.seek(0)

        embeddings[file["metadata"]["student_id"]] = np.load(
            stream,
            allow_pickle=False,
        )

    return embeddings
