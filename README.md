# AI Service
Independent FastAPI service for face detection, embedding generation, embedding storage, and attendance prediction.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

The first run downloads the InsightFace `buffalo_l` model pack. Use `DEVICE=cpu` for CPU inference or a non-CPU value with CUDA-capable ONNX Runtime providers available. The cosine `SIMILARITY_THRESHOLD` defaults to `0.45` and can be tuned in `.env`. `VERIFICATION_MAX_WORKERS` controls how many verification photos are processed in parallel and defaults to `5`.

## APIs

- `GET /health` returns service status.
- `POST /register-face` accepts `student_id`, `image`, and optional `scope`; saves `student_<id>.npy` under the scope folder when provided.
- `POST /verify-attendance` accepts one or more `images` files (legacy single `image` is also accepted) and optional `scope`; processes uploaded photos in parallel, compares detected faces only against embeddings in that scope, and returns present/absent records.

The model adapter is isolated in `app/face_engine.py` so InsightFace Buffalo_L can later be replaced by another implementation without changing Django or React.


## Run without backend/frontend

Use `register_student.py` and `verify_student.py` when you want to test the AI service locally without starting Django or React. Run them from the `ai-service/` directory after installing this service's requirements.

Register a single student image and create `../media/embeddings/SCH001/10/A/student_101.npy`:

```bash
python register_student.py --student-id 101 --scope SCH001/10/A --image ../media/students/student101.jpg
```

Verify one or more classroom images against existing local embeddings:

```bash
python verify_student.py --scope SCH001/10/A --image ../media/attendance/front.jpg ../media/attendance/back.jpg
```

Use the same `--scope` value for students and classroom photos in one school-code/class/section. Without `--scope`, the service falls back to the legacy global embeddings folder. `register_student.py` prints only the created-embedding JSON. `verify_student.py` prints only the same JSON shape as `POST /verify-attendance`, including `detected_faces`, `matches`, and each student's `Present`/`Absent` status; InsightFace provider/model logs are suppressed so the output can be parsed directly.
