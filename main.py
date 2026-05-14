##### Imports #####
from time import sleep

from leds import builtin_led
from sim_comms import initComms, pollComms
from sim_adcs import initADCS

##### Setup #####
initADCS()
initComms()

##### Loop #####
while True:
    builtin_led.toggle()
    pollComms()
    sleep(1)