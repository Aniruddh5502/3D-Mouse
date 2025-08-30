import serial
import csv
import time

# ---- Config ----
PORT = "COM3"        # Change to your ESP32 port (e.g., "/dev/ttyUSB0" on Linux/Mac)
BAUD = 1000000     # Must match ESP32 Serial.begin()
OUTFILE = "imu_log.csv"

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    # wait a bit for ESP32 reset 
    time.sleep(2)

    with open(OUTFILE, "w", newline="") as f:
        writer = csv.writer(f)

        # Read the header from ESP32 first
        header = ser.readline().decode(errors="ignore").strip()
        if header:
            writer.writerow(header.split(","))
            print("Header:", header)

        print("Logging... Press Ctrl-C to stop.")

        try:
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                fields = line.split(",")
                if len(fields) == 8:   # timestamp + 7 fields
                    writer.writerow(fields)
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            ser.close()

if __name__ == "__main__":
    main()
