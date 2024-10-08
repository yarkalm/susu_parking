# Используем базовый образ PyTorch с поддержкой CUDA
FROM anibali/pytorch:2.0.1-cuda11.8

# Устанавливаем зависимости Python
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Копируем ваш код в контейнер
COPY . /app
WORKDIR /app

RUN sudo chmod +x start.sh

# Настройка точки входа по умолчанию для запуска скриптов
CMD ["./start.sh"]

