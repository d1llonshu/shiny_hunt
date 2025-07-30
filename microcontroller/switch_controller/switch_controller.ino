#include "switch_ESP32.h"
NSGamepad Gamepad;

void setup() {
  Gamepad.begin();
  USB.begin();
}

void loop() {
  Gamepad.press(NSButton_A);
  Gamepad.write();
  delay(100);

  Gamepad.release(NSButton_A);
  Gamepad.write();
  delay(2000);

  Gamepad.press(NSButton_B);
  Gamepad.write();
  delay(100);
  
  Gamepad.release(NSButton_B);
  Gamepad.write();
  delay(2000);
  
}
