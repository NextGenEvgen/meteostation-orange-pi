import wiringpi
import dht11

# Инициализация WiringPi
wiringpi.wiringPiSetup()

# Чтение данных через pin 7
instance = dht11.DHT11(pin = 7)
result = instance.read()

if result.is_valid():
    print("Температура: %-3.1f C" % result.temperature)
    print("Влажность: %-3.1f %%" % result.humidity)
else:
    print("Ошибка: %d" % result.error_code)