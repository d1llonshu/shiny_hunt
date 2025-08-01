#include "switch_ESP32.h"
#include <cstring>  // for strcmp
NSGamepad Gamepad;
constexpr long COM_BAUD = 115200;

constexpr uint8_t NUM_INPUTS = 14;
constexpr uint16_t PRESS_TIME = 100;

// static const char* valid_inputs[NUM_INPUTS] = {
//   "A",
//   "B",
//   "X",
//   "Y",
//   "LeftTrigger",
//   "RightTrigger",
//   "LeftThrottle",
//   "RightThrottle",
//   "Minus",
//   "Plus",
//   "LeftStick",
//   "RightStick",
//   "Home",
//   "Capture"
// };
// uint16_t buttons[NUM_INPUTS] = {NSButton_A, NSButton_B, NSButton_X, NSButton_Y, 
//            NSButton_LeftTrigger, NSButton_RightTrigger,
//            NSButton_LeftThrottle, NSButton_RightThrottle,
//            NSButton_Minus, NSButton_Plus,
//            NSButton_LeftStick, NSButton_RightStick,
//            NSButton_Home, NSButton_Capture};


// int findInputIndex(const char* input) {
//   for (size_t i = 0; i < NUM_INPUTS; ++i) {
//     if (strcmp(valid_inputs[i], input) == 0) {
//       return int(i);
//     }
//   }
//   return -1;
// }


void buttonPress(uint8_t button, uint16_t hold_ms){
  Gamepad.press(button);
  Gamepad.write();
  delay(hold_ms);

  Gamepad.release(button);
  Gamepad.write();
}

void dPadPress(NSDirection_t direction, uint16_t hold_ms){
  Gamepad.dPad(direction);
  Gamepad.write();
  delay(hold_ms);

  Gamepad.dPad(NSGAMEPAD_DPAD_CENTERED);
  Gamepad.write();
}

void setup() {
  Gamepad.begin();
  USB.begin();
  Serial0.begin(COM_BAUD);
  delay(2000);
  buttonPress(NSButton_A, PRESS_TIME);
  delay(2000);

  buttonPress(NSButton_B, PRESS_TIME);
  delay(2000);
}

void shayminScript(){
  
}

void loop() {
  if (Serial0.available() > 0) {                // if data is waiting in buffer
        char cmd = Serial0.read();               // read one byte/char
        // decide action based on cmd:
        Serial0.println("input recieved:");
        Serial0.println(cmd);
        if (cmd == 'A') { buttonPress(NSButton_A, PRESS_TIME); }
        else if (cmd == 'B') { buttonPress(NSButton_B, PRESS_TIME); }
        else if (cmd == 'X') { buttonPress(NSButton_X, PRESS_TIME); }
        else if (cmd == 'Y') { buttonPress(NSButton_Y, PRESS_TIME); }

        else if (cmd == 'U') { dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME); }
        else if (cmd == 'D') { dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME); }
        else if (cmd == 'L') { dPadPress(NSGAMEPAD_DPAD_LEFT, PRESS_TIME); }
        else if (cmd == 'R') { dPadPress(NSGAMEPAD_DPAD_RIGHT, PRESS_TIME); }
  }
}
