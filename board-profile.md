# Board profile: Waveshare ESP32-S3-Touch-LCD-2.8

Hardware-verified profile used to build the Velxio board definition.

## Chip / module

| Property | Value |
|---|---|
| SoC | ESP32-S3 (Xtensa LX7, dual-core, up to 240 MHz) |
| Module | N16R8 → **16 MB flash**, **8 MB PSRAM (octal / OPI)** |
| USB | Native USB-C (CDC), enumerates as `/dev/ttyACM0` |
| Velxio family / QEMU | `esp32-s3` → `qemu-system-xtensa -M esp32s3` |
| Arduino FQBN (generic) | `esp32:esp32:esp32s3` |

## Velxio board options (see draft-pr/CHANGES.md → `getDefaultOptionsForKind`)

```
flashSize: '16MB'
psram:     'opi'      // octal PSRAM
cpuFreqMHz: 240
partitionScheme: 'min_spiffs'   // or a 16MB scheme
```

## Verified pinout

Read from the board's CircuitPython `board` module on real hardware (not from the
datasheet, which mislabels the touch chip). GPIO numbers are the ESP32-S3 IO numbers.

### LCD: ST7789, 240×320, SPI
| Signal | GPIO |
|---|---|
| MOSI | 45 |
| SCLK | 40 |
| CS | 42 |
| DC | 41 |
| RST | 39 |
| Backlight (BL) | 5 |
| MISO | none (not connected) |

### Touch: **CST3530 @ I²C 0x58** (NOT CST328/0x1A as the docs claim), dedicated I²C bus
| Signal | GPIO |
|---|---|
| SDA | 1 |
| SCL | 3 |
| INT | 4 |
| RST | 2 |

> Protocol note (for a future custom-chip model): 4-byte MSB-first commands, e.g. read =
> `D0 07 00 00`; frame valid when `buf[2]==0xFF`; touch count in `buf[3]&0x0F`; must send
> clear cmd `D0 00 02 AB` after each read or it latches.

### SD / TF card: SDMMC (exposed to CircuitPython as an SPI bus)
| Signal (SPI view) | GPIO |
|---|---|
| SCK / CLK | 14 |
| MOSI / CMD | 17 |
| MISO / D0 | 16 |
| CS / D3 | 21 |

### Shared I²C bus: QMI8658 IMU (0x6B) + PCF85063 RTC (0x51)
| Signal | GPIO |
|---|---|
| SDA | 11 |
| SCL | 10 |
| IMU INT1 / INT2 | 13 / 12 |

### I²S audio: PCM5101
| Signal | GPIO |
|---|---|
| BCK | 48 |
| DIN | 47 |
| LRCK | 38 |

### Misc
| Signal | GPIO |
|---|---|
| UART TX / RX | 43 / 44 |
| Boot button | 0 |
| Battery ADC | 8 |

## Simulation currently

- **Simulatable now:** the ESP32-S3 CPU + generic GPIO/SPI/I²C (real firmware runs in QEMU).
- **Maybe:** ST7789 via a generic TFT component wired to the LCD pins above.
- **Not without custom-chip work:** CST3530 touch, QMI8658, PCF85063, PCM5101.
