##### Imports #####
import sys
from time import sleep

from leds import builtin_led
from sim_comms import initComms, pollComms
from sim_adcs import initADCS
from sim_heatburn import initHeatburn

##### Setup #####
initADCS()
initComms()
initHeatburn()

##### Loop #####
while True:
    builtin_led.toggle()
    pollComms()
    sleep(1)