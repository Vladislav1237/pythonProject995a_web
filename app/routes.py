from flask import Blueprint, request, jsonify, render_template # Добавлено render_template
# import torch # torch должен быть установлен в requirements.txt

# Импортируем функции загрузки модели и токенизатора из соответствующих файлов
from .model import load_model
from .tokenizer import load_tokenizer

main_blueprint = Blueprint('main', __name__)

# Загружаем модель и токенизатор ОДИН РАЗ при старте приложения
# Внимание: если модели очень большие, это может вызвать OutOfMemory на PythonAnywhere Free Tier
try:
    model = load_model()
    tokenizer = load_tokenizer()
except Exception as e:
    print(f"Ошибка при загрузке модели/токенизатора: {e}")
    model = None # Установим None, чтобы избежать ошибок, если загрузка не удалась
    tokenizer = None


@main_blueprint.route('/')
def index():
    # Исправлено: теперь рендерит index.html
    return render_template('index.html')


@main_blueprint.route('/predict', methods=['POST'])
def predict():
    if model is None or tokenizer is None:
        return jsonify({'error': 'Модель или токенизатор не загружены. Попробуйте позже.'}), 503

    data = request.get_json()
    input_text = data.get('text', '')

    if not input_text:
        return jsonify({'response': 'Пожалуйста, введите текст для предсказания.'}), 400

    try:
        inputs = tokenizer(input_text, return_tensors="pt")
        # Возможно, вам понадобятся дополнительные параметры для generate(), например:
        # max_length=50, num_beams=5, early_stopping=True, no_repeat_ngram_size=2
        outputs = model.generate(**inputs)

        prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return jsonify({'response': prediction})
    except Exception as e:
        # Логирование ошибки для отладки
        print(f"Ошибка при генерации ответа: {e}")
        return jsonify({'response': f'Произошла ошибка при обработке запроса: {e}'}), 500