import wiringpi
import dht11

# Инициализация WiringPi
wiringpi.wiringPiSetup()

# Чтение данных через pin 7
instance = dht11.DHT11(pin = 7)

def read_data():
    result = instance.read()

    if result.is_valid():
        return result
    else:
        print("Ошибка: %d" % result.error_code)
        return None