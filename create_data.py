import cv2
import numpy as np
from PIL import Image
from os import listdir
from ultralytics import YOLO
import matplotlib.pyplot as plt
from time import strftime, localtime

model = YOLO('yolov8s.pt')
classes = [2, 3, 5, 7]


def undistort_image(image, camera_matrix, distortion_coeffs):
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w, h), 1, (w, h))
    undistorted_image = cv2.undistort(image, camera_matrix, distortion_coeffs, None, new_camera_matrix)
    return undistorted_image


video_path = "https://cdn.cams.is74.ru/hls/playlists/multivariant.m3u8?uuid=52062848-61de-4e39-8948-5ca14dcfcd0b&token=bearer-aa25824cdf8db4addcce63e4b6de4e44"
cap = cv2.VideoCapture(video_path)

mask = cv2.imread("result_images/mask.png")
frame_count = 1
show_frame = 500
alpha = 0.4
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    if success:
        frame_count -= 1
        camera_matrix = np.array([[2179, 0, 1433],
                                  [0, 2049, 606],
                                  [0, 0, 1]])
        distortion_coeffs = np.array([0.48787777, -3.47110869, -0.09418035, -0.03887175, 6.42096464])

        # Исправление искажения
        frame = undistort_image(frame, camera_matrix, distortion_coeffs)
        h, w = frame.shape[0], frame.shape[1]
        frame = frame[int(h * 0.409):int(h * 0.8), int(w * 0.08):int(w * 0.9)]  # focus frame only on parking
        frame = cv2.bitwise_and(frame, mask)
        if frame_count == 0:
            # Run YOLOv8 inference on the frame
            pred = model.predict(frame, classes=classes, imgsz=3200, iou=0.2, conf=0.5)[0]
            annotated_frame = frame.copy()
            w, h = annotated_frame.shape[1], annotated_frame.shape[0]

            for index, cls, box in zip(range(len(pred.boxes.xywhn)), pred.boxes.cls, pred.boxes.xywhn):
                x1, y1 = np.int32([(box[0] - box[2] / 2) * w, (box[1] - box[3] / 2) * h])
                x2, y2 = np.int32([(box[0] + box[2] - box[2] / 2) * w, (box[1] + box[3] - box[3] / 2) * h])

                if 1000 <= ((x2 - x1) * (y2 - y1)) <= 12000:
                    row = f"{int(cls)} {box[0]} {box[1]} {box[2]} {box[3]}"

                    if index % 3 == 0:
                        cv2.imwrite(f"dataset/val/images/{len(listdir('dataset/val/images'))}.jpg",
                                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        with open(f"dataset/val/labels/{len(listdir('dataset/val/labels'))}.txt", 'w') as f:
                            f.write(row)
                    else:
                        cv2.imwrite(f"dataset/train/images/{len(listdir('dataset/train/images'))}.jpg",
                                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        with open(f"dataset/train/labels/{len(listdir('dataset/train/labels'))}.txt", 'w') as f:
                            f.write(row)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color=[255, 0, 0],
                              thickness=2)
                cv2.putText(annotated_frame, str(index), (int(box[0] * w) - 10, int(box[1] * h)),
                            cv2.FONT_HERSHEY_PLAIN, 1,
                            [255, 0, 0], 2)
            curr_time = strftime('%d.%m.%y %H:%M:%S', localtime())
            cv2.putText(annotated_frame, curr_time, (annotated_frame.shape[1] - 350, annotated_frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_PLAIN, 2, [0, 255, 0], 2)
            annotated_frame = cv2.resize(annotated_frame, (800, 216))
            cv2.imshow('Create dataset', annotated_frame)
            frame_count = show_frame  # reset to zero value

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            continue
    else:
        break

cap.release()
cv2.destroyAllWindows()
