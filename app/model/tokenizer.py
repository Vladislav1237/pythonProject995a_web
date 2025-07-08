from transformers import GPT2Tokenizer
from config import Config

# Загружаем токенизатор
def load_tokenizer():
    tokenizer = GPT2Tokenizer.from_pretrained(Config.TOKENIZER_PATH)
    return tokenizer
