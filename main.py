from flask import Flask
import dht11_sensor as dht
app = Flask(__name__)

@app.route('/')
def root():
    result = dht.read_data()
    if result != None:
        return f'Температура: {result.temperature}C<br>Влажность: {result.humidity}%'
    return 'Ошибка сбора данных'

if __name__ == '__main__':
    app.run(host="0.0.0.0")