import cv2
import numpy as np
from ultralytics import YOLO
from time import strftime, localtime

# Load the YOLOv8 model
title = 'SUSU Parking'
seg_model = YOLO('yolov8s-seg.pt')
classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Open the video file
# camera "Интерсвязь" on SUSU
video_path = "https://cdn.cams.is74.ru/hls/playlists/multivariant.m3u8?uuid=52062848-61de-4e39-8948-5ca14dcfcd0b&token=bearer-aa25824cdf8db4addcce63e4b6de4e44"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
frame_count = 1
show_frame = 2500
alpha = 0.4
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    if success:
        frame_count -= 1
        h, w = frame.shape[0], frame.shape[1]
        frame = frame[int(h * 0.49):int(h * 0.895), int(w * 0.16):int(w * 0.87)]  # focus frame only on parking
        if frame_count == 0:
            # Run YOLOv8 inference on the frame
            annotated_frame = frame.copy()  # copy frame for save original frame
            overlay = frame.copy()
            seg_results = seg_model.predict(annotated_frame, classes=classes, imgsz=3200, iou=0.5, conf=0.3)

            curr_time = strftime('%Y.%m.%d %H:%M:%S', localtime())  # current local time
            # Visualize the results on the frame
            for index, (box, seg) in enumerate(zip(seg_results[0].boxes.xyxy, seg_results[0].masks.xy)):
                cv2.fillPoly(overlay, np.int32([seg]), (0, 0, 255, 255*alpha))
            annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)
            for index, (box, seg) in enumerate(zip(seg_results[0].boxes.xyxy, seg_results[0].masks.xy)):
                # draw bboxes
                cv2.rectangle(annotated_frame, np.int32([box[0], box[1]]), np.int32([box[2], box[3]]),
                              color=[0, 255, 0])
                # put text indexes
                cv2.putText(annotated_frame, str(index), (int(box[0] + box[2]) // 2 - 15, int(box[1] + box[3]) // 2),
                            cv2.FONT_HERSHEY_PLAIN, 1.5, [0, 255, 0], 2)
                # put time
                cv2.putText(annotated_frame, curr_time, (annotated_frame.shape[1] - 350, annotated_frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_PLAIN, 2, [0, 255, 0], 2)


            # Display the annotated frame
            cv2.imshow(title, annotated_frame)
            frame_count = show_frame  # reset to zero value

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.imwrite('result_images/annotated_frame.jpg', annotated_frame)
                cv2.imwrite('result_images/frame.jpg', frame)
                break
        else:
            if cv2.waitKey(1) & 0xFF == ord("q"):
                try:
                    cv2.imwrite('result_images/annotated_frame.jpg', annotated_frame)
                except ValueError as e:
                    print("Annotated frame is unavailable")
                cv2.imwrite('result_images/frame.jpg', frame)
                break
            continue
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window

cap.release()
cv2.destroyAllWindows()
