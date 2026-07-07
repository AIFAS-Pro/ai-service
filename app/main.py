from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.model_loader import get_face_engine, load_face_engine
from app.recognition import (
    register_student_face,
    verify_attendance_images,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load the face model once before serving requests."""
    load_face_engine()
    yield


app = FastAPI(
    title="AI Attendance Face Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "running"}


@app.post("/register-face")
async def register_face(
    school_id: str = Form(...),
    student_id: str = Form(...),
    academic_year: str = Form(...),
    image: UploadFile = File(...),
) -> dict[str, str]:
    try:
        image_bytes = await image.read()

        if not image_bytes:
            raise HTTPException(
                status_code=422,
                detail="Image is empty.",
            )

        return register_student_face(
            face_engine=get_face_engine(),
            school_id=school_id.strip(),
            student_id=student_id.strip(),
            academic_year=academic_year.strip(),
            image_bytes=image_bytes,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        ) from exc


@app.post("/verify-attendance")
async def verify_attendance(
    school_id: str = Form(...),
    academic_year: str = Form(...),
    images: list[UploadFile] = File(...),
    student_ids: str | None = Form(default=None),
) -> dict[str, object]:
    try:
        image_bytes_list = [
            await uploaded_image.read()
            for uploaded_image in images
        ]

        if not image_bytes_list:
            raise HTTPException(
                status_code=422,
                detail="At least one attendance image is required.",
            )

        parsed_student_ids: list[str] | None = None

        if student_ids and student_ids.strip():
            parsed_student_ids = [
                student_id.strip()
                for student_id in student_ids.split(",")
                if student_id.strip()
            ]

            if not parsed_student_ids:
                parsed_student_ids = None

        return verify_attendance_images(
            face_engine=get_face_engine(),
            school_id=school_id.strip(),
            academic_year=academic_year.strip(),
            student_ids=parsed_student_ids,
            image_bytes_list=image_bytes_list,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        ) from exc