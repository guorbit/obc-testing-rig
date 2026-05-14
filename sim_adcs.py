from machine import I2CTarget, Pin

# Response bank
not_ready_response = b"Adcs not ready"
nofix_response = b"t00:00:00|N+00.00000|E+000.10000|h+000.00m|f0|c0032.73|b100858|i0|a+002.38-005.52+007.89|q+000.47-000.05-000.34+000.81|m+005.62+025.56-054.1"

# Set which response to send for testing.  
response = nofix_response

# Global index for response
response_index = 0

def initADCS():
    # I2C target on pins GP4 and GP5, address 0x42
    single_byte = bytearray(1)

    i2c_target = I2CTarget(id=0, addr=0x08, scl=Pin(5), sda=Pin(4))

    # IRQ handler for I2C read requests.
    # This sends one byte at a time when the master reads from the target.
    def i2c_irq_handler(i2c_target):
        global response_index
        flags = i2c_target.irq().flags()

        if flags & I2CTarget.IRQ_ADDR_MATCH_READ:
            response_index = 0

        if flags & I2CTarget.IRQ_READ_REQ:
            if response_index < len(response):
                single_byte[0] = response[response_index]
                response_index += 1
            else:
                single_byte[0] = 0
            i2c_target.write(single_byte)

    irq_triggers = I2CTarget.IRQ_ADDR_MATCH_READ | I2CTarget.IRQ_READ_REQ
    i2c_target.irq(i2c_irq_handler, trigger=irq_triggers, hard=True)