import numpy as np
import cv2
import glob

# Ширина и высота шахматной доски (в количестве внутренних углов)
board_width = 17
board_height = 11


board_size = (board_width, board_height)

# Создание массива для хранения углов доски в каждом изображении
obj_points = []  # 3D координаты углов в мировой системе координат
img_points = []  # 2D координаты углов на изображении

# Генерация координат углов шахматной доски
objp = np.zeros((board_height*board_width, 3), np.float32)
objp[:, :2] = np.mgrid[0:board_width, 0:board_height].T.reshape(-1, 2)

# Загрузка изображений с шахматными досками
images = glob.glob('result_images/full_big_chess.png')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Поиск углов шахматной доски
    ret, corners = cv2.findChessboardCorners(gray, board_size, None)

    # Если углы найдены, добавляем их в массив
    if ret == True:
        obj_points.append(objp)
        img_points.append(corners)

        # Отображаем углы на изображении
        img = cv2.drawChessboardCorners(img, board_size, corners, ret)
        cv2.imshow('img', img)
        if cv2.waitKey() & 0xFF == ord("q"):
            break

cv2.destroyAllWindows()

# Калибровка камеры
ret, camera_matrix, distortion_coeffs, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

# Вывод результатов калибровки
print("Camera Matrix:")
print(np.int32(camera_matrix))
print("\nDistortion Coefficients:")
print(distortion_coeffs)
