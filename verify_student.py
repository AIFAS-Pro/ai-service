#!/usr/bin/env python
"""Verify attendance directly inside the AI service without Django or React.

Examples:
    python verify_student.py --image ../media/attendance/2026-06-29/classroom.jpg
    python verify_student.py --image ../media/attendance/front.jpg ../media/attendance/back.jpg
    python verify_student.py --register --student-id 101 --image ../media/students/student101.jpg
"""

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Register or verify faces using only the AI service code."
    )
    parser.add_argument(
        "--image",
        required=True,
        nargs="+",
        help="Path to one or more classroom images, or one student image when --register is used.",
    )
    parser.add_argument(
        "--register",
        action="store_true",
        help="Register one student face instead of verifying attendance against existing embeddings.",
    )
    parser.add_argument(
        "--student-id", help="Student ID required when --register is used."
    )
    parser.add_argument(
        "--scope",
        help="Optional school-code/class/section scope, for example SCH001/10/A.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_paths = [Path(image) for image in args.image]
    missing_paths = [
        image_path for image_path in image_paths if not image_path.is_file()
    ]
    if missing_paths:
        raise SystemExit(f"Image file not found: {missing_paths[0]}")
    if args.register and not args.student_id:
        raise SystemExit("--student-id is required when --register is used")
    if args.register and len(image_paths) != 1:
        raise SystemExit("Exactly one --image path is allowed when --register is used")

    from app.model_loader import get_face_engine
    from app.recognition import register_student_face, verify_attendance_images

    face_engine = get_face_engine()
    image_bytes_list = [image_path.read_bytes() for image_path in image_paths]

    if args.register:
        result = register_student_face(
            face_engine, args.student_id, image_bytes_list[0], scope=args.scope
        )
    else:
        result = verify_attendance_images(
            face_engine, image_bytes_list, scope=args.scope
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
