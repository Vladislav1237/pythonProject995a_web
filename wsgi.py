import sys
import os
from . import create_app # Исправлено: относительный импорт

# Убедитесь, что 'а' в конце - это латинская 'a', а не кириллическая 'а'
sys.path.insert(0, '/home/Vladislav1234/pythonProject995a')

application = create_app() # Рекомендация PythonAnywhere: переменная должна называться 'application'