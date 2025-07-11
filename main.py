"""
Node C (Sensor) - Environmental Sensing with Deep Sleep
Performs temperature/humidity sensing and power monitoring with deep sleep optimization
"""

import sys
sys.path.append('/lib')

from machine import I2C, Pin, deepsleep, reset_cause, DEEPSLEEP_RESET
import time
import json
from ina219 import INA219
# from dht22 import DHT22  # DHT22を使用しない
from espnow_helper import ESPNowHelper
import esp32

# 使用するピン（RTC対応ピン）
wake_pin = Pin(33, mode=Pin.IN, pull=Pin.PULL_DOWN)
wake_end_pin = Pin(19, mode=Pin.OUT, pull=Pin.PULL_DOWN)
# EXT0で外部信号によるWakeupを設定（HIGHで起動）
esp32.wake_on_ext0(pin=wake_pin, level=esp32.WAKEUP_ANY_HIGH)

class NodeCSensor:
    def __init__(self):
        
        # Timing parameters
        self.active_time_ms = 5000  # Stay active for 1 second
        self.default_sleep_time_ms = 5000  # Default sleep time
        
        # Load persistent settings
        self.load_settings()
        
        # Initialize I2C for INA219
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        
        # Initialize INA219 power monitor
        try:
            self.ina219 = INA219(self.i2c, address=0x40)
            self.ina219.set_calibration_32v_2a()
            print("INA219 initialized")
        except Exception as e:
            print(f"INA219 init error: {e}")
            self.ina219 = None
        
        # DHT22は使用しない - ダミーデータを生成
        self.dht22 = None
        print("Using dummy sensor data (DHT22 disabled)")
        
        # Initialize ESP-NOW communication
        self.espnow = ESPNowHelper(channel=1)
        print(f"Node C MAC: {self.espnow.get_mac_address()}")
        
        # Add Node B as peer (replace with actual MAC)
        self.node_b_mac = self.espnow.add_peer("ac:67:b2:2a:7e:88", "Node_B")
        self.node_ce_mac = self.espnow.add_peer("78:21:84:9d:1b:00", "Node_CE")
        
        # Boot information
        self.boot_count = self.get_boot_count()
        print(f"Node C Boot #{self.boot_count}")
        
        
        print("Node C (Sensor) initialized")
    
    def get_boot_count(self):
        """Get boot count from file"""
        try:
            with open('boot_count.txt', 'r') as f:
                count = int(f.read().strip())
        except:
            count = 0
        
        count += 1
        
        if count == 1:
            self.espnow.send_jikken_start(self.node_ce_mac)
            print("start")
        
        try:
            with open('boot_count.txt', 'w') as f:
                f.write(str(count))
                
        except:
            pass
            
        return count
    
    def load_settings(self):
        """Load persistent settings from file"""
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.sensing_enabled = settings.get('sensing_enabled', True)
                self.current_sleep_time_ms = settings.get('sleep_time_ms', 20000)
                print(f"Settings loaded: enabled={self.sensing_enabled}, sleep={self.current_sleep_time_ms}ms")
        except:
            # Default settings
            self.sensing_enabled = True
            self.current_sleep_time_ms = self.default_sleep_time_ms
            print("Using default settings")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'sensing_enabled': self.sensing_enabled,
                'sleep_time_ms': self.current_sleep_time_ms
            }
            with open('settings.json', 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Settings save error: {e}")
    
    def measure_power_consumption(self):
        """Measure and log current power consumption"""
        if not self.ina219:
            return
            
        try:
            bus_voltage = self.ina219.get_bus_voltage()
            shunt_voltage = self.ina219.get_shunt_voltage()
            current_ma = self.ina219.get_current()
            power_mw = self.ina219.get_power()
            timestamp = time.ticks_ms()
            
            print(f"NODE_C_POWER,{bus_voltage:.2f},{current_ma:.2f},{power_mw:.2f},{shunt_voltage:.2f},{timestamp}")
            
        except Exception as e:
            print(f"Power measurement error: {e}")
    
    def read_sensors(self):
        """Read environmental sensors (dummy data)"""
        # ダミーデータを生成
        import random
        
        # 現実的な範囲でランダムな値を生成
        base_temp = 25.0  # 基準温度 25°C
        base_humidity = 60.0  # 基準湿度 60%
        
        # ±3°C、±10%の範囲でランダムに変動
        temperature = base_temp + random.uniform(-3.0, 3.0)
        humidity = base_humidity + random.uniform(-10.0, 10.0)
        
        # 範囲制限
        temperature = max(-40.0, min(80.0, temperature))
        humidity = max(0.0, min(100.0, humidity))
        
        print(f"Dummy sensor data: T={temperature:.1f}°C, H={humidity:.1f}%")
        
        return temperature, humidity
    
    def send_sensor_data(self):
        """Read sensors and send data"""
        if not self.sensing_enabled:
            print("Sensing disabled, skipping data collection")
            return
        
        print("Reading sensors...")
        
        # Read environmental sensors
        temperature, humidity = self.read_sensors()
        
        # Read power measurements
        voltage = 0.0
        current = 0.0
        power = 0.0
        
        if self.ina219:
            try:
                voltage = self.ina219.get_bus_voltage()
                current = self.ina219.get_current()
                power = self.ina219.get_power()
            except Exception as e:
                print(f"Power read error: {e}")
        
        # Prepare sensor data
        sensor_data = {
            "type": "sensor_data",
            "temperature": temperature,
            "humidity": humidity,
            "voltage": voltage,
            "current": current,
            "power": power,
            "timestamp": time.ticks_ms(),
            "boot_count": self.boot_count
        }
        
        # Send to Node B
        success = self.espnow.send_data(sensor_data, self.node_b_mac)
        if success:
            print(f"Sensor data sent: T={temperature:.1f}°C, H={humidity:.1f}%, V={voltage:.2f}V")
        else:
            print("Failed to send sensor data")
    
    def check_control_messages(self, duration_ms):
        """Check for control messages from Node A"""
        start_time = time.ticks_ms()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < duration_ms:
            sender_mac, data = self.espnow.receive_data(timeout_ms=50)
            
            if sender_mac and data and isinstance(data, dict):
                if data.get("type") == "control":
                    self.process_control_message(data)
    
    def process_control_message(self, data):
        """Process control message from Node A"""
        interval_ms = data.get("sensing_interval_ms")
        enabled = data.get("sensing_enabled")
        
        settings_changed = False
        
        if enabled is not None and enabled != self.sensing_enabled:
            self.sensing_enabled = enabled
            settings_changed = True
            print(f"Sensing {'enabled' if enabled else 'disabled'}")
        
        if interval_ms and interval_ms >= 1000:
            new_sleep_time = max(interval_ms - self.active_time_ms, 1000)
            if new_sleep_time != self.current_sleep_time_ms:
                self.current_sleep_time_ms = new_sleep_time
                settings_changed = True
                print(f"Sleep time updated to {self.current_sleep_time_ms}ms")
        
        if settings_changed:
            self.save_settings()
    
    def enter_deep_sleep(self):
        """Enter deep sleep mode"""
        print(f"Entering deep sleep for {self.current_sleep_time_ms} ms")
        
        # Cleanup ESP-NOW
        self.espnow.deinit()
        
        # Enter deep sleep
        #deepsleep(self.current_sleep_time_ms)
        wake_end_pin.value(0)
        deepsleep()
    
    def run(self):
        """Main execution cycle"""
        start_time = time.ticks_ms()
        
        # Check for control messages
        remaining_time = self.active_time_ms - time.ticks_diff(time.ticks_ms(), start_time)
        if remaining_time > 0:
            print(f"Listening for control messages ({remaining_time}ms)...")
            self.check_control_messages(remaining_time - 100)  # Leave 100ms buffer
        
        # Wait for remaining active time
        elapsed_time = time.ticks_diff(time.ticks_ms(), start_time)
        remaining_time = max(self.active_time_ms - elapsed_time, 0)
        
        if remaining_time > 0:
            print(f"Waiting {remaining_time}ms before sleep...")
            time.sleep_ms(remaining_time)
        
        # Enter deep sleep
        self.enter_deep_sleep()

def main():
    """Entry point"""
    try:
        node_c = NodeCSensor()
        wake_end_pin.value(1)
        node_c.run()
    except Exception as e:
        print(f"Node B error: {e}")
        # If there's an error, wait a bit then reset
        time.sleep(5)
        import machine
        machine.reset()

if __name__ == "__main__":
    main()