import pandas as pd
import numpy as np
import allantools
import matplotlib.pyplot as plt

# -------- Load Converted Data --------
df = pd.read_csv("imu_log_converted.csv")

# Rename for clarity (optional, but keeps things consistent)
df = df.rename(columns={
    "ax": "accel_x",
    "ay": "accel_y",
    "az": "accel_z",
    "gx": "gyro_x",
    "gy": "gyro_y",
    "gz": "gyro_z",
    "temp_raw": "temperature"
})

# -------- Parameters --------
fs = 1000       # Hz (adjust to your IMU sampling rate)
n_points = 1000 # number of log-spaced tau points
min_tau = 1     # smallest averaging window in samples
max_fraction = 0.1  # tau max length relative to dataset size

def compute_adev(data, fs, min_tau=1, max_fraction=0.1, n_points=1000):
    """
    Compute Allan deviation with log-spaced taus.
    """
    N = len(data)
    max_tau = int(N * max_fraction) / fs   # sec
    taus = np.logspace(np.log10(min_tau/fs), np.log10(max_tau), n_points)

    taus, adevs, _, _ = allantools.adev(
        data,
        rate=fs,
        data_type="freq",
        taus=taus
    )
    return taus, adevs

def calculate_allan_parameters(taus, adevs, sensor_type="gyro"):
    """
    Calculate Allan variance parameters from tau and adev arrays.
    
    Parameters:
    - taus: array of tau values (averaging times)
    - adevs: array of Allan deviation values
    - sensor_type: "gyro" or "accel" for appropriate parameter naming
    
    Returns:
    - Dictionary with calculated parameters
    """
    
    # 1. Random Walk (ARW for gyro, VRW for accel)
    # Found in white noise region (slope = -0.5 on log-log plot)
    # Calculate from early points: Random_Walk = adev * sqrt(tau)
    random_walk = adevs[0] * np.sqrt(taus[0])
    
    # 2. Bias Instability
    # Minimum value of the Allan deviation curve (flat region)
    bias_instability = np.min(adevs)
    
    # 3. Averaging Time
    # Tau value at which bias instability occurs
    min_idx = np.argmin(adevs)
    averaging_time = taus[min_idx]
    
    # 4. Bias Drift Onset
    # Point where curve starts rising after minimum (random walk region)
    bias_drift_onset = taus[-1]  # Default to end if no clear onset
    
    # Find where adev becomes significantly larger than minimum
    threshold = bias_instability * 1.3  # 30% increase threshold
    for i in range(min_idx + 1, len(adevs)):
        if adevs[i] > threshold:
            bias_drift_onset = taus[i]
            break
    
    return {
        "random_walk": random_walk,
        "bias_instability": bias_instability,
        "averaging_time": averaging_time,
        "bias_drift_onset": bias_drift_onset
    }

def print_parameters(axis, params, sensor_type):
    """Print formatted parameter results"""
    if sensor_type == "gyro":
        rw_name = "Angle Random Walk (ARW)"
        rw_units = "rad/√s"
        bias_units = "rad/s"
    else:
        rw_name = "Velocity Random Walk (VRW)"
        rw_units = "m/s²/√Hz"
        bias_units = "m/s²"
    
    print(f"\n{axis.upper()}:")
    print(f"  {rw_name}: {params['random_walk']:.3e} {rw_units}")
    print(f"  Bias Instability: {params['bias_instability']:.3e} {bias_units}")
    print(f"  Averaging Time: {params['averaging_time']:.2f} s")
    print(f"  Bias Drift Onset: {params['bias_drift_onset']:.2f} s")

# -------- Gyroscope Allan Deviation Analysis --------
print("=" * 60)
print("GYROSCOPE ALLAN VARIANCE PARAMETERS")
print("=" * 60)

plt.figure(figsize=(8, 6))
gyro_data = {}
for axis in ["gyro_x", "gyro_y", "gyro_z"]:
    taus, adevs = compute_adev(df[axis].to_numpy(), fs, min_tau, max_fraction, n_points)
    plt.loglog(taus, adevs, label=axis, linewidth=2)
    
    # Store data and calculate parameters
    gyro_data[axis] = {"taus": taus, "adevs": adevs}
    params = calculate_allan_parameters(taus, adevs, sensor_type="gyro")
    
    # Print parameters
    print_parameters(axis, params, "gyro")

plt.xlabel("Tau (s)")
plt.ylabel("Allan Deviation (rad/s)")
plt.title("Gyroscope Allan Deviation")
plt.legend()
plt.grid(True, which="both", alpha=0.3)
plt.savefig("gyro_allan.png", dpi=300, bbox_inches='tight')
plt.show()

# -------- Accelerometer Allan Deviation Analysis --------
print("\n" + "=" * 60)
print("ACCELEROMETER ALLAN VARIANCE PARAMETERS")
print("=" * 60)

plt.figure(figsize=(8, 6))
accel_data = {}
for axis in ["accel_x", "accel_y", "accel_z"]:
    taus, adevs = compute_adev(df[axis].to_numpy(), fs, min_tau, max_fraction, n_points)
    plt.loglog(taus, adevs, label=axis, linewidth=2)
    
    # Store data and calculate parameters
    accel_data[axis] = {"taus": taus, "adevs": adevs}
    params = calculate_allan_parameters(taus, adevs, sensor_type="accel")
    
    # Print parameters
    print_parameters(axis, params, "accel")

plt.xlabel("Tau (s)")
plt.ylabel("Allan Deviation (m/s²)")
plt.title("Accelerometer Allan Deviation")
plt.legend()
plt.grid(True, which="both", alpha=0.3)
plt.savefig("accel_allan.png", dpi=300, bbox_inches='tight')
plt.show()

# -------- Summary Table --------
print("\n" + "=" * 80)
print("SUMMARY TABLE")
print("=" * 80)

print("\nGYROSCOPE PARAMETERS:")
print("-" * 50)
print(f"{'Axis':<8} {'ARW (rad/√s)':<15} {'Bias Inst.(rad/s)':<18} {'Avg Time(s)':<12} {'Drift Onset(s)':<15}")
print("-" * 50)
for i, axis in enumerate(["gyro_x", "gyro_y", "gyro_z"]):
    taus, adevs = gyro_data[axis]["taus"], gyro_data[axis]["adevs"]
    params = calculate_allan_parameters(taus, adevs, sensor_type="gyro")
    print(f"{axis:<8} {params['random_walk']:<15.3e} {params['bias_instability']:<18.3e} "
          f"{params['averaging_time']:<12.2f} {params['bias_drift_onset']:<15.2f}")

print("\nACCELEROMETER PARAMETERS:")
print("-" * 55)
print(f"{'Axis':<8} {'VRW (m/s²/√Hz)':<16} {'Bias Inst.(m/s²)':<17} {'Avg Time(s)':<12} {'Drift Onset(s)':<15}")
print("-" * 55)
for i, axis in enumerate(["accel_x", "accel_y", "accel_z"]):
    taus, adevs = accel_data[axis]["taus"], accel_data[axis]["adevs"]
    params = calculate_allan_parameters(taus, adevs, sensor_type="accel")
    print(f"{axis:<8} {params['random_walk']:<16.3e} {params['bias_instability']:<17.3e} "
          f"{params['averaging_time']:<12.2f} {params['bias_drift_onset']:<15.2f}")

plt.show()