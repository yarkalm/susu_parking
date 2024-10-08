import cv2
import numpy as np
from ultralytics import YOLO
from time import strftime, localtime


def undistort_image(image, camera_matrix, distortion_coeffs):
    h, w = image.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w, h), 1, (w, h))
    undistorted_image = cv2.undistort(image, camera_matrix, distortion_coeffs, None, new_camera_matrix)
    return undistorted_image


# Функция для проверки пересечения двух прямоугольников
def is_overlapping(rect1, rect2):
    x1, y1, x2, y2 = rect1
    x1_, y1_, x2_, y2_ = rect2
    # Возвращает True, если прямоугольники пересекаются
    return not (x2 <= x1_ or x1 >= x2_ or y2 <= y1_ or y1 >= y2_)


# Load the YOLOv8 model
title = 'SUSU Parking'
seg_model = YOLO('yolov8s-seg.pt')
seg_model.to('cpu')
classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Open the video file
# camera "Интерсвязь" on SUSU
video_path = "https://cdn.cams.is74.ru/hls/playlists/multivariant.m3u8?uuid=52062848-61de-4e39-8948-5ca14dcfcd0b&token=bearer-aa25824cdf8db4addcce63e4b6de4e44"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
mask = cv2.imread("result_images/mask.png")
park_ico = cv2.imread("parking.png")
park_ico = cv2.cvtColor(park_ico, cv2.COLOR_RGBA2RGB)

i_h, i_w = park_ico.shape[0], park_ico.shape[1]
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

        if frame_count == 0:
            # Run YOLOv8 inference on the frame
            annotated_frame = frame.copy()  # copy frame for save original frame
            overlay = frame.copy()
            h, w = annotated_frame.shape[0], annotated_frame.shape[1]

            seg_results = seg_model.predict(cv2.bitwise_and(annotated_frame, mask), classes=classes, imgsz=6400,
                                            iou=0.2, conf=0.1)

            curr_time = strftime('%d.%m.%y %H:%M:%S', localtime())  # current local time
            # Visualize the results on the frame
            contours, _ = cv2.findContours(cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY), cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
            free_space = cv2.fillPoly(overlay.copy(), contours, (0, 255, 0, 255 * alpha))
            for index, (box, seg) in enumerate(zip(seg_results[0].boxes.xyxy, seg_results[0].masks.xy)):
                cv2.fillPoly(overlay, np.int32([seg]), (0, 0, 255, 255 * alpha))
                cv2.fillPoly(free_space, np.int32([seg]), (0, 0, 0))
            # Наложение overlay на annotated_frame с прозрачностью alpha
            annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)
            annotated_frame = cv2.addWeighted(free_space, alpha, annotated_frame, 1 - alpha, 0)

            for index, (box, seg) in enumerate(zip(seg_results[0].boxes.xyxy, seg_results[0].masks.xy)):
                # draw bboxes
                box = box.cpu().numpy()
                cv2.rectangle(annotated_frame, np.int32([box[0], box[1]]), np.int32([box[2], box[3]]),
                              color=[0, 255, 0])
                # put text indexes
                cv2.putText(annotated_frame, str(index), (int(box[0] + box[2]) // 2 - 15, int(box[1] + box[3]) // 2),
                            cv2.FONT_HERSHEY_PLAIN, 1.5, [0, 255, 0], 2)
                # put time
                cv2.putText(annotated_frame, curr_time, (annotated_frame.shape[1] - 350, annotated_frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_PLAIN, 2, [0, 255, 0], 2)

            # Список прямоугольников, которые содержат только белые пиксели
            white_rects = []

            x = 0  # начальная координата x
            y = 0  # начальная координата y

            # Скользящее окно по изображению
            while y < h - 50:
                while x < w:
                    # Выбираем размер прямоугольника в зависимости от высоты
                    if (int(h * 0.28) < y < int(h * 0.39) and int(w * 0.15) < x < int(w * 0.865)) or (
                            int(h * 0.65 - 40) < y < int(h * 0.78) and int(w * 0.02) < x < int(w * 0.95)) or (
                            int(h * 0.84) < y < int(h) and int(w * 0.065) < x < int(w * 1)):
                        rect_height = 60
                        rect_width = 110
                    elif int(h * 0.4) < y < int(h * 0.6):
                        rect_height = 70
                        rect_width = 50
                    else:
                        rect_height = 60
                        rect_width = 47
                    # Извлечение подмаски
                    submask = free_space[y:y + rect_height, x:x + rect_width]

                    # Проверка, содержит ли область только белые пиксели
                    if np.all(submask == (0, 255, 0)):
                        new_rect = (x, y, x + rect_width, y + rect_height)

                        # Проверка, не пересекается ли с существующими прямоугольниками
                        overlapping = any(is_overlapping(new_rect, existing) for existing in white_rects)

                        if not overlapping:
                            white_rects.append(new_rect)  # Добавление в список
                            x += rect_width  # Двигаемся к следующей позиции
                        else:
                            x += 10  # Перемещаемся немного вправо, если пересекается
                    else:
                        x += 5  # Если не только белые пиксели, двигаемся вправо

                # Обновляем координаты для следующей строки
                x = 0
                y += 5  # Перемещаемся на один пиксель вниз

            overlay_parking = annotated_frame.copy()
            parking_boxes = frame.copy()
            parking_lots = frame.copy()
            for rect in white_rects:
                x1, y1, x2, y2 = rect

                cv2.rectangle(overlay_parking, (x1, y1), (x2, y2), (255, 0, 0), -1)
                cv2.rectangle(overlay_parking, (x1, y1), (x2, y2), (0, 0, 255), 2)

                cv2.rectangle(parking_boxes, (x1, y1), (x2, y2), (0, 255, 0), -1)
                cv2.rectangle(parking_boxes, (x1, y1), (x2, y2), (0, 0, 255), 2)

                # Adjust bounds
                x2 = min(x2, w)
                y2 = min(y2, h)

                # Determine scaling factor for icon
                rect_width = x2 - x1
                rect_height = y2 - y1
                scale_factor = min(rect_width / i_w, rect_height / i_h)

                # Resize park_ico while maintaining proportions
                resized_park_ico = cv2.resize(
                    park_ico,
                    (int(i_w * scale_factor), int(i_h * scale_factor))
                )

                # Coordinates for resized icon in parking_lots
                icon_height, icon_width = resized_park_ico.shape[:2]
                y_start = y1
                x_start = x1
                y_end = y1 + icon_height
                x_end = x1 + icon_width

                # Check if within bounds
                if x_end <= w and y_end <= h:
                    parking_lots[y_start:y_end, x_start:x_end, :] = resized_park_ico

            annotated_frame = cv2.addWeighted(overlay_parking, alpha, annotated_frame, 1 - alpha, 0)
            parking_boxes = cv2.addWeighted(parking_boxes, alpha, frame.copy(), 1 - alpha, 0)
            cv2.putText(parking_boxes, curr_time, (parking_boxes.shape[1] - 350, parking_boxes.shape[0] - 10),
                        cv2.FONT_HERSHEY_PLAIN, 2, [0, 255, 0], 2)
            cv2.putText(parking_lots, curr_time, (parking_lots.shape[1] - 350, parking_lots.shape[0] - 10),
                        cv2.FONT_HERSHEY_PLAIN, 2, [0, 255, 0], 2)

            # Display the annotated frame
            # cv2.imshow(title + ' Annotate',
            #            cv2.resize(annotated_frame, (annotated_frame.shape[1] // 2, annotated_frame.shape[0] // 2)))
            cv2.imwrite('result_images/annotated_frame.jpg', annotated_frame)

            # cv2.imshow(title + ' Bboxes', cv2.resize(parking_boxes, (parking_boxes.shape[1]//2, parking_boxes.shape[0]//2)))
            cv2.imwrite('result_images/parking_boxes.jpg', parking_boxes)

            # cv2.imshow(title + ' Icons', cv2.resize(parking_lots, (parking_lots.shape[1]//2, parking_lots.shape[0]//2)))
            cv2.imwrite('result_images/parking_lots.jpg', parking_lots)
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
