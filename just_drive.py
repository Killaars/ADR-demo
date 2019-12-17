from overdrive import Overdrive

# Global variables for the cars and the directionchange
# Select which cars to use on the track using MAC address of the device
#car2 = Overdrive("CD:5A:27:DC:41:89") #Brandbaar
#car3 = Overdrive("DE:83:21:EB:1B:2E") #GAS
car3 = Overdrive("FB:76:00:CB:82:63") #Explosief
car2 = Overdrive("DB:DE:FF:52:CB:9E") #Radioactief

initial_car_speed = 300
initial_car_acceleration = 800
car2.changeSpeed(initial_car_speed, initial_car_acceleration)
car3.changeSpeed(initial_car_speed, initial_car_acceleration)