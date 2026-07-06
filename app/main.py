from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from app.model_loader import get_face_engine, load_face_engine
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.recognition import register_student_face, verify_attendance_images


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Load the face model once before serving register/verify requests."""
    load_face_engine()
    yield


app = FastAPI(title="AI Attendance Face Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "running"}


@app.post("/register-face")
async def register_face(
    student_id: str = Form(...),
    image: UploadFile = File(...),
    scope: str | None = Form(default=None),
) -> dict[str, str]:
    try:
        return register_student_face(
            get_face_engine(), student_id, await image.read(), scope=scope
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/verify-attendance")
async def verify_attendance(
    images: list[UploadFile] = File(...),
    scope: str | None = Form(default=None),
) -> dict[str, object]:
    try:
        image_bytes = [await uploaded_image.read() for uploaded_image in images]

        return verify_attendance_images(
            get_face_engine(),
            image_bytes,
            scope=scope,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
