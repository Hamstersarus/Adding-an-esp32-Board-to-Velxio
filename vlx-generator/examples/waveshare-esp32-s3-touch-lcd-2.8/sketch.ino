// Waveshare ESP32-S3-Touch-LCD-2.8 - custom board pinout under test
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

// The custom board's LCD pinout (verified on real hardware)
#define TFT_SCK  40
#define TFT_MOSI 45
#define TFT_MISO 46   // not wired on the real board; harmless in sim
#define TFT_CS   42
#define TFT_DC   41
#define TFT_RST  39
#define TFT_BL    5

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

void setup() {
  Serial.begin(115200);
  pinMode(TFT_BL, OUTPUT);
  digitalWrite(TFT_BL, HIGH);
  SPI.begin(TFT_SCK, TFT_MISO, TFT_MOSI, TFT_CS);
  tft.begin();
  tft.setRotation(1);
  tft.fillScreen(ILI9341_NAVY);
  tft.setCursor(24, 60);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(3);
  tft.println("Waveshare S3");
  tft.setCursor(24, 130);
  tft.setTextColor(ILI9341_YELLOW);
  tft.setTextSize(2);
  tft.println("custom pinout test");
  Serial.println("drawn");
}

void loop() { delay(2000); }
