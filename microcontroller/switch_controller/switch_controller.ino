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

// void comboPress(uint8_t button, NSDirection_t direction, uint16_t hold_ms){
//   Gamepad.press(button);
//   Gamepad.dPad(direction);
//   Gamepad.write();

//   delay(hold_ms);

//   Gamepad.release(button);
//   Gamepad.dPad(NSGAMEPAD_DPAD_CENTERED);
//   Gamepad.write();
// }

// void shayminScript(char step){
// // Run from battle
//   Serial0.write("Beginning Scripted Inputs");
//   dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME);
//   buttonPress(NSButton_A, PRESS_TIME);
  
//   // Wait for "Shaymin disappeared into the flowers"
//   delay(5000); //could shorten a little, maybe down to 4.75, mightve failed last time
  
//   buttonPress(NSButton_A, PRESS_TIME);

//   // Sprint down 3.25
//   Gamepad.press(NSButton_B);
//   Gamepad.dPad(NSGAMEPAD_DPAD_DOWN);
//   Gamepad.write();

//   delay(3250); 

//   // Sprint up for 3.5
//   Gamepad.release(NSButton_B);
//   Gamepad.dPad(NSGAMEPAD_DPAD_CENTERED);
//   Gamepad.write();

//   Gamepad.press(NSButton_B);
//   Gamepad.dPad(NSGAMEPAD_DPAD_UP);
//   Gamepad.write();

//   delay(3500); //sometimes for some reason it doesnt run up enough so
  
//   Gamepad.release(NSButton_B);
//   Gamepad.dPad(NSGAMEPAD_DPAD_CENTERED);
//   Gamepad.write();

//   // Begin Shaymin fight
//   buttonPress(NSButton_A, PRESS_TIME);
//   delay(3000); //wait for animation to be done
//   buttonPress(NSButton_A, PRESS_TIME);

//   Serial0.write("Starting Battle");
//   delay(5500);
//   Serial0.write("Start Shiny Check");
//   delay(3500);
//   Serial0.write("Screenshot");
//   delay(6500);
//   Serial0.write("End Shiny Check");
//   delay(3750); //could almost certainly be faster by a few seconds (maybe 2) (cut 1.25 already) (cant cut more i dont think because of occasional breelom friendship action)
//   Serial0.write("End Scripted Input");
// }

void bdsp_reset(char step) {
  //in battle -> close game -> start game
  if (step == '1'){
    Serial0.write("Resetting");
    buttonPress(NSButton_Home, PRESS_TIME);
    delay(500);
    buttonPress(NSButton_X, PRESS_TIME);
    delay(500);
    buttonPress(NSButton_A, PRESS_TIME);
    Serial0.write("Pressing A");
    delay(750);
    buttonPress(NSButton_A, PRESS_TIME);
    delay(750);
    buttonPress(NSButton_A, PRESS_TIME);
    delay(2000); //Waiting out the animation from the switch on game startup, excess time here is fine
    Serial0.write("Starting Darkness Check");
  }
  //start game -> palkia/dialga animation
  else if (step == '2') {
    Serial0.write("Ending Darkness Check"); //need a write here because the ser_log needs to be updated in the video_parser.py
    delay(2500);//can't press the button immediately
    Serial0.write("Pressing A Button");
    //While a center bounding box is pitch black, wait (wait 25 seconds technically)
    buttonPress(NSButton_A, PRESS_TIME);
    delay(3000);
    buttonPress(NSButton_A, PRESS_TIME);
    delay(3000); //Wait for animation to finish before starting check, excess time here is fine
    Serial0.write("Starting Darkness Check");
    //wait until the center box isnt pitch black again.
  }
}

//Upload thru COM8, unplug, plug USB port into Switch, plug COM8 in again.
//Unplug from switch to upload

void loop() {
  if (Serial0.available() > 0) {                // if data is waiting in buffer
        // char cmd = Serial0.read();               // read one byte/char
        // decide action based on cmd:
        // Serial0.println("input recieved:");
        
        // shayminScript(cmd);
        char step = Serial0.read();
        Serial0.println(step);
        if (step == '1'){
          bdsp_reset('1');
        }
        else if (step == '2') {
          bdsp_reset('2');
        }
        else if (step == '3') {
          //after load
          //dpad up
          //wait 14
          Serial0.write("Ending Darkness Check");
          delay(1000); //Wait for game to fully load
          dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME);
          delay(13000);//cutscene
          buttonPress(NSButton_A, PRESS_TIME);
          // wait 10-12 (12 probably upper bound)
          Serial0.write("Starting Battle");
          delay(4500);
          Serial0.write("Starting Shiny Check");
          delay(3500);
          Serial0.write("Screenshotting");
          delay(5500);
          Serial0.write("Ending Shiny Check");
          delay(4000); //could almost certainly be faster by a few seconds (maybe 2) (cut 1.25 already) (cant cut more i dont think because of occasional breelom friendship action)
          Serial0.write("Ending Scripted Input");
          //shiny check
        }
        else if (step == 'A') { buttonPress(NSButton_A, PRESS_TIME); }
        else if (step == 'B') { buttonPress(NSButton_B, PRESS_TIME); }
        else if (step == 'X') { buttonPress(NSButton_X, PRESS_TIME); }
        else if (step == 'Y') { buttonPress(NSButton_Y, PRESS_TIME); }

        else if (step == 'U') { dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME); }
        else if (step == 'D') { dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME); }
        else if (step == 'L') { dPadPress(NSGAMEPAD_DPAD_LEFT, PRESS_TIME); }
        else if (step == 'R') { dPadPress(NSGAMEPAD_DPAD_RIGHT, PRESS_TIME); }
        // if (cmd == 'A') { buttonPress(NSButton_A, PRESS_TIME); }
        // else if (cmd == 'B') { buttonPress(NSButton_B, PRESS_TIME); }
        // else if (cmd == 'X') { buttonPress(NSButton_X, PRESS_TIME); }
        // else if (cmd == 'Y') { buttonPress(NSButton_Y, PRESS_TIME); }

        // else if (cmd == 'U') { dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME); }
        // else if (cmd == 'D') { dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME); }
        // else if (cmd == 'L') { dPadPress(NSGAMEPAD_DPAD_LEFT, PRESS_TIME); }
        // else if (cmd == 'R') { dPadPress(NSGAMEPAD_DPAD_RIGHT, PRESS_TIME); }
  }
}
