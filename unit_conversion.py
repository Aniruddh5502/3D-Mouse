import pandas as pd
import numpy as np

# Load raw data
df = pd.read_csv("imu_log.csv")

# Conversion factors (MPU6050, datasheet)
ACCEL_SCALE = 16384.0     # LSB/g for ±2g
GYRO_SCALE = 131.0        # LSB/(°/s) for ±250 dps
G_TO_MS2 = 9.80665
DEG2RAD = np.pi / 180.0

# Convert raw to physical units
df["ax"] = df["ax"] / ACCEL_SCALE * G_TO_MS2       # m/s²
df["ay"] = df["ay"] / ACCEL_SCALE * G_TO_MS2
df["az"] = df["az"] / ACCEL_SCALE * G_TO_MS2

df["gx"] = df["gx"] / GYRO_SCALE * DEG2RAD         # rad/s
df["gy"] = df["gy"] / GYRO_SCALE * DEG2RAD
df["gz"] = df["gz"] / GYRO_SCALE * DEG2RAD

df["temp_raw"] = df["temp_raw"] / 340.0 + 36.53    # °C

# Save back with same columns
df.to_csv("imu_log_converted.csv", index=False)

print("Converted data saved to imu_log_converted.csv")
print(df.head())
