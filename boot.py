#Deepsleepからの復帰時間の測定用

import sys
sys.path.append('/lib')
from ina219 import INA219
from machine import Pin, I2C
import time
from espnow_helper import ESPNowHelper


recv_peer = "ac:67:b2:2a:7e:88"
wake_output = Pin(23, Pin.OUT, pull=Pin.PULL_DOWN)
wake_input = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)

interval = 5

def write_power():
    I2C_INTERFACE_NO = 2
    SHUNT_OHMS = 0.1  # Check value of shunt used with your INA219
    
    with open("power.csv", "w") as f:
        pass

    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    ina219 = INA219(i2c, address=0x40)
    ina219.set_calibration_32v_2a()
    write_count = 0
    next_time = time.ticks_add(time.ticks_ms(), 100)
    with open("power.csv", "a") as f:
        f.write("timestamp,mA,V,mW\n")
    
    while write_count < 600:
        if time.ticks_diff(time.ticks_ms(), next_time) < 0:
            continue
        
        next_time = time.ticks_add(time.ticks_ms(), 100)
            
        try:
            timestamp = time.localtime()
            timestamp_str = "{:04}:{:02}:{:02}:{:02}:{:02}:{:02}".format(*timestamp[:6])
            bus_voltage = ina219.get_bus_voltage()
            shunt_voltage = ina219.get_shunt_voltage()
            current_ma = ina219.get_current()
            power_mw = ina219.get_power()
            
            with open("power.csv", "a") as f:
                f.write(f"{timestamp_str},{current_ma:.2f},{bus_voltage:.2f},{power_mw:.2f}\n")
            
        except Exception as e:
            print(f"Power measurement error: {e}")
        
        write_count += 1


def write_wake_time():
    while True:
        wake_output.value(1)
        start = time.ticks_ms()
        while True:
            if wake_input.value():
                end = time.ticks_ms()
                wake_time = time.ticks_diff(end, start)
                with open("wake_time.csv", "a") as f:
                    f.write(f"{wake_time}\n")
                break
            
            else:
                continue
        
        while True:
            if wake_input.value() == 0:
                wake_output.value(0)
                time.sleep(interval)
                break

# メイン非同期タスク
def main():
    p2 = Pin(2, Pin.OUT)
    p2.on()
    try:
        write_wake_time()
    finally:
        p2.off()


if __name__ == "__main__":
    main()
    
