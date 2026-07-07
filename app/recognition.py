import numpy as np
from concurrent.futures import ThreadPoolExecutor
from app.config import settings
from app.face_engine import FaceEngine
from app.gridfs_storage import (
    save_embedding,
    delete_embedding,
    load_embeddings,
)


def register_student_face(
    face_engine: FaceEngine,
    school_id: str,
    student_id: str,
    academic_year: str,
    image_bytes: bytes,
) -> dict[str, str]:

    embeddings = face_engine.image_to_embeddings(image_bytes)

    if len(embeddings) != 1:
        raise ValueError(
            "Registration image must contain exactly one detectable face."
        )

    delete_embedding(
        school_id=school_id,
        student_id=student_id,
        academic_year=academic_year,
    )

    save_embedding(
        school_id=school_id,
        student_id=student_id,
        academic_year=academic_year,
        embedding=embeddings[0],
    )

    return {
        "status": "success",
        "school_id": school_id,
        "student_id": student_id,
        "academic_year": academic_year,
        "storage": "gridfs",
    }


def load_known_embeddings(
    school_id: str,
    academic_year: str,
    student_ids: list[str] | None = None,
) -> dict[str, np.ndarray]:
    return load_embeddings(
        school_id=school_id,
        academic_year=academic_year,
        student_ids=student_ids,
    )


def verify_attendance_image(
    face_engine: FaceEngine,
    image_bytes: bytes,
    school_id: str,
    academic_year: str,
    student_ids: list[str] | None = None,
) -> dict[str, object]:
    return verify_attendance_images(
        face_engine=face_engine,
        image_bytes_list=[image_bytes],
        school_id=school_id,
        academic_year=academic_year,
        student_ids=student_ids,
    )


def verify_attendance_images(
    face_engine: FaceEngine,
    image_bytes_list: list[bytes],
    school_id: str,
    academic_year: str,
    student_ids: list[str] | None = None,
) -> dict[str, object]:

    if not image_bytes_list:
        raise ValueError("At least one attendance image is required.")

    known_embeddings = load_known_embeddings(
        school_id=school_id,
        academic_year=academic_year,
        student_ids=student_ids,
    )

    if not known_embeddings:
        raise ValueError("No registered student embeddings were found.")

    image_results = _extract_embeddings_in_parallel(
        face_engine,
        image_bytes_list,
    )

    present_ids: set[str] = set()
    matches: list[dict[str, object]] = []

    for image_index, detected_embeddings in enumerate(image_results):
        for face_index, embedding in enumerate(detected_embeddings):

            best_student_id = None
            best_score = 0.0

            for known_student_id, known_embedding in known_embeddings.items():

                score = face_engine.best_similarity(
                    embedding,
                    [known_embedding],
                )

                if score > best_score:
                    best_score = score
                    best_student_id = known_student_id

            if (
                best_student_id is not None
                and best_score >= settings.similarity_threshold
            ):
                present_ids.add(best_student_id)

                matches.append(
                    {
                        "image_index": image_index,
                        "face_index": face_index,
                        "student_id": best_student_id,
                        "similarity": round(best_score, 4),
                    }
                )

    students = [
        {
            "student_id": student_id,
            "status": "Present" if student_id in present_ids else "Absent",
        }
        for student_id in sorted(known_embeddings)
    ]

    return {
        "status": "success",
        "school_id": school_id,
        "academic_year": academic_year,
        "image_count": len(image_bytes_list),
        "detected_faces": sum(
            len(embeddings)
            for embeddings in image_results
        ),
        "images": [
            {
                "image_index": image_index,
                "detected_faces": len(embeddings),
            }
            for image_index, embeddings in enumerate(image_results)
        ],
        "matches": matches,
        "students": students,
    }


def _extract_embeddings_in_parallel(
    face_engine: FaceEngine,
    image_bytes_list: list[bytes],
) -> list[list[np.ndarray]]:

    max_workers = min(
        len(image_bytes_list),
        settings.verification_max_workers,
    )

    if max_workers <= 1:
        return [
            face_engine.image_to_embeddings(image_bytes)
            for image_bytes in image_bytes_list
        ]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(
            executor.map(
                face_engine.image_to_embeddings,
                image_bytes_list,
            )
        )