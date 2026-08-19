// Pin map for the Waveshare ESP32-S3-Touch-LCD-2.8 in Velxio.
// Paste into frontend/src/utils/boardPinMapping.ts (see CHANGES.md §3).
//
// Maps board silk/function labels -> ESP32-S3 GPIO numbers.
// Verified on real hardware (CircuitPython `board` module + I2C scan).
// The touch controller is a CST3530 @ 0x58 (NOT the CST328/0x1A in the datasheet).

export const WAVESHARE_S3_TOUCH_28_MAP: Record<string, number> = {
  // LCD - ST7789, SPI
  LCD_MOSI: 45,
  LCD_SCLK: 40,
  LCD_CS: 42,
  LCD_DC: 41,
  LCD_RST: 39,
  LCD_BL: 5,

  // Touch - CST3530, dedicated I2C bus (addr 0x58)
  TP_SDA: 1,
  TP_SCL: 3,
  TP_INT: 4,
  TP_RST: 2,

  // SD / TF card - SDMMC (SPI view)
  SD_SCK: 14,
  SD_MOSI: 17,
  SD_MISO: 16,
  SD_CS: 21,

  // Shared I2C - QMI8658 IMU (0x6B) + PCF85063 RTC (0x51)
  I2C_SDA: 11,
  I2C_SCL: 10,
  IMU_INT1: 13,
  IMU_INT2: 12,

  // I2S audio - PCM5101
  I2S_BCK: 48,
  I2S_DIN: 47,
  I2S_LRCK: 38,

  // Misc
  TX: 43,
  RX: 44,
  BOOT: 0,
  BAT_ADC: 8,
};
