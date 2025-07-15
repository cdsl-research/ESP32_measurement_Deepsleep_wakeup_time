#Deepsleepからの復帰時間の測定用

from machine import Pin, I2C
import time

wake_output = Pin(2, Pin.OUT, pull=Pin.PULL_DOWN)
wake_input = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)

interval = 5

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
    write_wake_time()


if __name__ == "__main__":
    main()
    
