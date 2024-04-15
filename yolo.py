import cv2
import numpy as np
from ultralytics import YOLO

title = 'SUSU Parking'
# Load the YOLOv8 model
model = YOLO('yolov8s.pt')

# Open the video file
video_path = "https://cdn.cams.is74.ru/hls/playlists/multivariant.m3u8?uuid=52062848-61de-4e39-8948-5ca14dcfcd0b&token=bearer-aa25824cdf8db4addcce63e4b6de4e44"
cap = cv2.VideoCapture(video_path)
cv2.namedWindow(title, cv2.WINDOW_NORMAL)
cv2.resizeWindow(title, 1200, 500)
# Loop through the video frames

frame_count = 0
show_frame = 60
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    print(frame_count)
    if success:
        frame_count += 1
        if frame_count % show_frame == 0:
            h, w = frame.shape[0], frame.shape[1]
            frame = frame[int(h * 0.495):int(h * 0.875), int(w * 0.15):int(w * 0.85)]
            # Run YOLOv8 inference on the frame
            results = model(frame)

            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow(title, annotated_frame)
            frame_count = 0

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.imwrite('frame.jpg', frame)
                break
        else:
            continue
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window

cap.release()
cv2.destroyAllWindows()
