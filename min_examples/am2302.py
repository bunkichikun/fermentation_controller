import time
import board
import adafruit_dht
import math

dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=True)


while True:
    try:
        temperature = dhtDevice.temperature
        humidite = dhtDevice.humidity

        print("temperature: " + str(temperature))
        print("humidite: " + str(humidite))




#        # calcul du point de rosée  (formule de Heinrich Gustav Magnus-Tetens)
#        alpha = math.log(humidite / 100.0) + (17.27 * temperature) / (237.3 + temperature)
#        rosee = (237.3 * alpha) / (17.27 - alpha)

        #calcul de l'humidex
 #       humidex = temperature + 0.5555 * (6.11 * math.exp(5417.753 * (1 / 273.16 - 1 / (273.15 + rosee))) - 10)

  #      print("Temperature:  {:.1f} C    Humidite: {}%     Rosee:  {:.1f} C     Humidex:  {:.1f}"
  #            .format(temperature , humidite, rosee , humidex))


    except RuntimeError as error:
        print(error.args[0])
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error

    time.sleep(2)

