import logging
import os
from flask import Flask, render_template, abort
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import dht11_sensor as dht

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Защита от DDoS: ограничение запросов (10 в минуту на IP)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"]
)

# Декоратор для валидации данных сенсора
def validate_sensor_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if result is None:
                logger.warning("Датчик ничего не отправил")
                return None
            # Проверка диапазонов значений
            if not (-50 <= result.temperature <= 80):
                logger.error(f"Некорректная температура: {result.temperature}")
                return None
            if not (0 <= result.humidity <= 100):
                logger.error(f"Некорректная влажность: {result.humidity}")
                return None
            return result
        except Exception as e:
            logger.error(f"Ошибка при проверке значений с датчика: {e}")
            return None
    return wrapper

@app.route('/')
@limiter.limit("10 per minute")
@validate_sensor_data 
def root():
    try:
        result = dht.read_data()
        if result is not None:
            # Экранирование данных перед передачей в шаблон (защита от XSS)
            temperature = float(f"{result.temperature:.1f}")
            humidity = float(f"{result.humidity:.1f}")
            logger.info(f"Показания датчика: T={temperature}°C, H={humidity}%")
            return render_template(
                'index.html',
                temperature=temperature,
                humidity=humidity,
                error=None
            )
        else:
            logger.error("Ошибка при чтении данный с датчика")
            return render_template('index.html', temperature=None, humidity=None, error="Ошибка сбора данных с датчика")
    except Exception as e:
        logger.critical(f"Неизвестная ошибка: {e}")
        abort(500)

# Обработка ошибок
@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(f"Превышен лимит запросов: {e.description}")
    return "Превышен лимит запросов. Попробуйте позже.", 429

@app.errorhandler(500)
def internal_error(e):
    logger.critical(f"Внутренняя ошибка сервера: {e}")
    return "Внутренняя ошибка сервера", 500

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    ssl_context = None
    if os.path.exists('cert.pem') and os.path.exists('key.pem'):
        ssl_context = ('cert.pem', 'key.pem')

    app.run(
        host=host,
        port=port,
        debug=debug,
        ssl_context=ssl_context
    )