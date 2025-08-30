#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const uint32_t SAMPLE_PERIOD_US = 1000; // 1 kHz = 1000 µs per sample

void setup() {
  Serial.begin(1000000);   // use a fast baud rate (1M+ recommended)
  while (!Serial) delay(10);

  Wire.begin();
  Wire.setClock(400000); // 400 kHz I2C

  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1) delay(1000);
  }

  // Set ranges
  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);   // ±2g
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);   // ±250 dps
  mpu.setDLPFMode(MPU6050_DLPF_BW_256);              // LPF ~256 Hz (reasonable for 1 kHz sample)
  // mpu.setRate(0); // internal rate divider (optional)

  // Header line
  Serial.println("timestamp_us,ax,ay,az,gx,gy,gz,temp_raw");

  delay(500);
}

void loop() {
  static uint32_t next_ts = esp_timer_get_time();

  int16_t ax, ay, az, gx, gy, gz;
  int16_t temp_raw;

  // Busy-wait until next sample time
  uint32_t now;
  do { now = esp_timer_get_time(); } while ((int32_t)(now - next_ts) < 0);
  next_ts += SAMPLE_PERIOD_US;

  // Read IMU data
  mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  temp_raw = mpu.getTemperature();

  // Stream CSV
  Serial.print(now);
  Serial.print(',');
  Serial.print(ax); Serial.print(',');
  Serial.print(ay); Serial.print(',');
  Serial.print(az); Serial.print(',');
  Serial.print(gx); Serial.print(',');
  Serial.print(gy); Serial.print(',');
  Serial.print(gz); Serial.print(',');
  Serial.println(temp_raw);
}
