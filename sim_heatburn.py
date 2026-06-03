from machine import Pin

burnwire, heater = None, None

def heatburn_handler(pin):
    global burnwire, heater

    if pin == burnwire:
        pin_name = "Burnwire (Pin 26)"
    elif pin == heater:
        pin_name = "Heater (Pin 27)"
    else:
        pin_name = f"Unknown Pin ({pin})"

    if pin.value() == 1:
        edge = "RISING (HIGH)"
    else:
        edge = "FALLING (LOW)"

    print(f"[HEATBURN] {pin_name} state changed to: {edge}")


def initHeatburn(): 
    global burnwire, heater 

    burnwire = Pin(26, Pin.IN, Pin.PULL_DOWN)
    heater = Pin(27, Pin.IN, Pin.PULL_DOWN)

    burnwire.irq(handler=heatburn_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)
    heater.irq(handler=heatburn_handler, trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING)


