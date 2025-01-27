from flask import Flask, render_template
import dht11_sensor as dht
app = Flask(__name__)

@app.route('/')
def root():
    result = dht.read_data()
    if result != None:
        return render_template('index.html', temperature=result.temperature, humidity=result.humidity)
    return 'Ошибка сбора данных'

if __name__ == '__main__':
    app.run(host="0.0.0.0")