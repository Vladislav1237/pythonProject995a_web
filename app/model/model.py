import os
from transformers import GPT2LMHeadModel
from config import Config # Исправлено: импортируем Config

def load_model():
    # Исправлено: используем путь из Config
    model = GPT2LMHeadModel.from_pretrained(Config.MODEL_PATH)
    return model

# Функция load_tokenizer удалена, так как она определена в tokenizer.py