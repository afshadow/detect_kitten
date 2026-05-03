from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


MODEL_FILES = (
    "deploy.prototxt",
    "mobilenet_iter_73000.caffemodel",
)

VOC_CLASSES = (
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
)
CAT_CLASS_ID = VOC_CLASSES.index("cat")


def ensure_model_files(model_dir: Path) -> tuple[Path, Path]:
    prototxt_path = model_dir / MODEL_FILES[0]
    weights_path = model_dir / MODEL_FILES[1]
    missing_files = [path.name for path in (prototxt_path, weights_path) if not path.is_file()]

    if missing_files:
        raise FileNotFoundError(
            "Local model files were not found in "
            f"{model_dir}. Missing: {', '.join(missing_files)}"
        )

    return prototxt_path, weights_path


def load_detector(prototxt_path: Path, weights_path: Path) -> cv2.dnn.Net:
    net = cv2.dnn.readNetFromCaffe(str(prototxt_path), str(weights_path))
    if net.empty():
        raise RuntimeError(
            f"Failed to load detector from {prototxt_path} and {weights_path}"
        )
    return net


def detect_cats(frame, detector: cv2.dnn.Net, confidence_threshold: float):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),
        scalefactor=0.007843,
        size=(300, 300),
        mean=127.5,
    )
    detector.setInput(blob)
    predictions = detector.forward()

    detections: list[tuple[int, int, int, int, float]] = []
    scale = np.array([width, height, width, height], dtype=np.float32)

    for index in range(predictions.shape[2]):
        confidence = float(predictions[0, 0, index, 2])
        class_id = int(predictions[0, 0, index, 1])
        if class_id != CAT_CLASS_ID or confidence < confidence_threshold:
            continue

        start_x, start_y, end_x, end_y = (
            predictions[0, 0, index, 3:7] * scale
        ).astype(int)
        start_x = max(start_x, 0)
        start_y = max(start_y, 0)
        end_x = min(end_x, width - 1)
        end_y = min(end_y, height - 1)

        if end_x <= start_x or end_y <= start_y:
            continue

        detections.append((start_x, start_y, end_x, end_y, confidence))

    return detections


def annotate_frame(frame, detections) -> int:
    for start_x, start_y, end_x, end_y, confidence in detections:
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (30, 210, 30), 2)
        cv2.putText(
            frame,
            f"Cat {confidence:.2f}",
            (start_x, max(start_y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (30, 210, 30),
            2,
        )

    count = len(detections)
    cv2.putText(
        frame,
        f"Cats detected: {count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
    )
    return count


def run_camera_mode(args, detector: cv2.dnn.Net) -> None:
    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open camera with index {args.camera_index}")

    print("Camera started. Press 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame from camera.")
            break

        detections = detect_cats(frame, detector, args.confidence)
        annotate_frame(frame, detections)
        cv2.imshow("Cat Detector", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def run_image_mode(args, detector: cv2.dnn.Net) -> None:
    image_path = Path(args.image).expanduser()
    frame = cv2.imread(str(image_path))
    if frame is None:
        raise FileNotFoundError(f"Failed to read image: {image_path}")

    detections = detect_cats(frame, detector, args.confidence)
    count = annotate_frame(frame, detections)
    print(f"Cats detected: {count}")

    if args.save:
        output_path = Path(args.save).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(output_path), frame):
            raise RuntimeError(f"Failed to save output image: {output_path}")
        print(f"Saved result to: {output_path}")

    if not args.no_display:
        cv2.imshow("Cat Detector", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect full cats in a webcam feed or on a single image."
    )
    parser.add_argument(
        "--image",
        help="Path to an input image. If omitted, webcam mode is used.",
    )
    parser.add_argument(
        "--save",
        help="Path to save the annotated image when --image is used.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Do not open an OpenCV window in image mode.",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Camera index for webcam mode. Default: 0",
    )
    parser.add_argument(
        "--model-dir",
        default=str(Path(__file__).resolve().parent / "models"),
        help="Directory where the detector model files are stored.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.35,
        help="Minimum confidence for cat detections. Default: 0.35",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    prototxt_path, weights_path = ensure_model_files(Path(args.model_dir).expanduser())
    detector = load_detector(prototxt_path, weights_path)

    if args.image:
        run_image_mode(args, detector)
    else:
        run_camera_mode(args, detector)


if __name__ == "__main__":
    main()
