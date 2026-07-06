#!/usr/bin/env python
"""Register a student face directly inside the AI service.

This script does not start or call Django, React, or the FastAPI server. It loads
InsightFace Buffalo_L locally, extracts exactly one face embedding from the supplied
student image, and saves it as `student_<student_id>.npy` in the configured
embeddings directory or scoped class/section subdirectory.

Example:
    python register_student.py --student-id 101 --scope SCH001/10/A --image ../media/students/student101.jpg
"""

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a student face embedding using only the AI service code.")
    parser.add_argument("--student-id", required=True, help="Student ID used in the embedding filename.")
    parser.add_argument("--image", required=True, help="Path to a student image containing exactly one face.")
    parser.add_argument("--scope", help="Optional school-code/class/section scope, for example SCH001/10/A.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    if not image_path.is_file():
        raise SystemExit(f"Image file not found: {image_path}")

    from app.model_loader import get_face_engine
    from app.recognition import register_student_face

    result = register_student_face(get_face_engine(), args.student_id, image_path.read_bytes(), scope=args.scope)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
