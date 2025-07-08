import os

class Config:
    # Замените эти заглушки на АБСОЛЮТНЫЕ ПУТИ к вашим сохраненным моделям и токенизаторам на PythonAnywhere.
    # Например: '/home/Vladislav1234/pythonProject995a/models/gpt2_model'
    # ИЛИ установите эти переменные окружения на PythonAnywhere.
    MODEL_PATH = os.getenv("MODEL_PATH", "/home/Vladislav1234/pythonProject995a/my_gpt2_model") # Пример реального пути
    TOKENIZER_PATH = os.getenv("TOKENIZER_PATH", "/home/Vladislav1234/pythonProject995a/my_gpt2_tokenizer") # Пример реального пути

    # Для безопасности всегда используйте сильный, случайный ключ
    SECRET_KEY = os.getenv("SECRET_KEY", "ваша_очень_длинная_и_сложная_секретная_строка")