from flask import Flask
from .routes import main_blueprint # Корректный относительный импорт

def create_app():
    app = Flask(__name__)

    # Регистрация маршрутов
    app.register_blueprint(main_blueprint)

    # Здесь можно добавить другие конфигурации, например:
    # app.config.from_object(Config) # Если хотите загружать Config сюда

    return app