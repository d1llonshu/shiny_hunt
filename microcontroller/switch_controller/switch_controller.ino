#include "switch_ESP32.h"
#include <cstring>  // for strcmp
NSGamepad Gamepad;
constexpr long COM_BAUD = 115200;

constexpr uint8_t NUM_INPUTS = 14;

//in MS
constexpr uint16_t PRESS_TIME = 100;
constexpr uint16_t SHORT_PRESS_TIME = 50;
constexpr uint16_t NO_MENU_DELAY = 100;

//16 bit (0-255)
constexpr uint8_t STICK_MIN = 0;
constexpr uint8_t STICK_MAX = 255;
constexpr uint8_t STICK_NEUTRAL = 128;

//{x,y}
constexpr uint8_t STICK_LEFT[2] = {STICK_MIN, STICK_NEUTRAL};
constexpr uint8_t STICK_RIGHT[2] = {STICK_MAX, STICK_NEUTRAL};
constexpr uint8_t STICK_UP[2] = {STICK_NEUTRAL, STICK_MIN};
constexpr uint8_t STICK_DOWN[2] = {STICK_NEUTRAL, STICK_MAX};


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

  // delay(NO_MENU_DELAY);
}

void dPadPress(NSDirection_t direction, uint16_t hold_ms){
  Gamepad.dPad(direction);
  Gamepad.write();
  delay(hold_ms);

  Gamepad.dPad(NSGAMEPAD_DPAD_CENTERED);
  Gamepad.write();

  // delay(NO_MENU_DELAY);
}

//x and y rest at 128
//array len not enforced
void leftStickPress(const uint8_t arr[2], uint16_t hold_ms){
  Gamepad.leftXAxis(arr[0]);
  Gamepad.leftYAxis(arr[1]);
  Gamepad.write();
  delay(hold_ms);

  Gamepad.leftXAxis(128);
  Gamepad.leftYAxis(128);
  Gamepad.write();

  // delay(NO_MENU_DELAY);
}
void rightStickPress(const uint8_t arr[2], uint16_t hold_ms){
  Gamepad.rightXAxis(arr[0]);
  Gamepad.rightYAxis(arr[1]);
  Gamepad.write();
  delay(hold_ms);

  Gamepad.rightXAxis(128);
  Gamepad.rightYAxis(128);
  Gamepad.write();

  // delay(NO_MENU_DELAY);
}

void comboPress(uint8_t button, NSDirection_t direction, uint16_t hold_ms){
  Gamepad.press(button);
  Gamepad.dPad(direction);
  Gamepad.write();
  delay(hold_ms);

  Gamepad.release(button);
  Gamepad.dPad(NSGAMEPAD_DPAD_CENTERED);
  Gamepad.write();

  // delay(NO_MENU_DELAY);
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

// void cresselia_reset(char step) {
//   else if (step == '3') {
//       //after load
//       //dpad up
//       //wait 14
//       Serial0.write("Ending Darkness Check");
//       delay(1000); //Wait for game to fully load
//       dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME);
//       buttonPress(NSButton_A, PRESS_TIME);
//       delay(5500);//cutscene
//       buttonPress(NSButton_A, PRESS_TIME);
//       delay(250);
//       buttonPress(NSButton_A, PRESS_TIME);
//       delay(750);
//       buttonPress(NSButton_A, PRESS_TIME);
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_DOWN, 3000);
//       delay(3000);
//       Serial0.write("Opening Menu");
//       //open menu
//       buttonPress(NSButton_X, PRESS_TIME);
//       delay(1000);
//       // dPadPress(NSGAMEPAD_DPAD_RIGHT, PRESS_TIME);
//       buttonPress(NSButton_A, PRESS_TIME);
//       delay(1000);
//       dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME);
//       buttonPress(NSButton_A, PRESS_TIME);
//       delay(500);
//       dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME);
//       buttonPress(NSButton_A, PRESS_TIME);
//       Serial0.write("Teleporting");

//       delay(11500);
//       Serial0.write("Teleport Done");
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_LEFT, 750);
//       delay(200);
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_DOWN, 3250);
//       // leftStickPress(STICK_LEFT, 750);
//       // delay(NO_MENU_DELAY);
//       // leftStickPress(STICK_DOWN, 3250);
//       delay(NO_MENU_DELAY);
//       buttonPress(NSButton_RightTrigger, 250);
//       delay(NO_MENU_DELAY);
//       Serial0.write("S Roaming");
//       delay(1250);
//       Serial0.write("E I Roaming");
//       delay(250);
      
//       //shiny check
//     }
//     //loop for roaming
//     else if (step == '4') {
//       // comboPress(NSButton_B, NSGAMEPAD_DPAD_UP, 250);
//       dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME);
//       dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME);
//       delay(200);
//       dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME);
//       dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME);
//       // delay(250);
//       Serial0.write("S Roaming");
//       delay(1100);
//       Serial0.write("E Roaming");
//       delay(150);
//     }
//     else if (step == '5'){
//       Serial0.write("Applying Repel");
//       buttonPress(NSButton_X, PRESS_TIME);
//       //Wait for menu to open, should be on pokemon because of teleport
//       delay(1000);
//       dPadPress(NSGAMEPAD_DPAD_RIGHT, SHORT_PRESS_TIME);
//       delay(NO_MENU_DELAY);//even though there is a menu
//       buttonPress(NSButton_A, SHORT_PRESS_TIME);
//       //wait for bag to open
//       delay(1300);
//       rightStickPress(STICK_RIGHT, 1000);
//       delay(NO_MENU_DELAY);//even though there is a menu
//       buttonPress(NSButton_A, SHORT_PRESS_TIME);//select
//       delay(250);
//       buttonPress(NSButton_A, SHORT_PRESS_TIME);//use
//       delay(500);
//       buttonPress(NSButton_B, SHORT_PRESS_TIME);//remove dialogue
//       delay(250);
//       buttonPress(NSButton_B, SHORT_PRESS_TIME);//back to X screen
//       delay(850); //closing menu is faster
//       buttonPress(NSButton_B, SHORT_PRESS_TIME);//back to game
//       delay(550); //closing menu is faster
//       //Wait for menu to close
//       Serial0.write("Walking to Grass");
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_DOWN, 750);
//       delay(NO_MENU_DELAY);
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_RIGHT, 750);
//       // leftStickPress(STICK_DOWN, 750);
//       // delay(NO_MENU_DELAY);
//       // leftStickPress(STICK_RIGHT, 750);
//       Serial0.write("In Grass");
//       delay(500);
//     }
//     else if (step == '6'){
//       delay(200);
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_RIGHT, 375);
//       delay(200);
//       comboPress(NSButton_B, NSGAMEPAD_DPAD_LEFT, 375);
//       delay(200);
//       // leftStickPress(STICK_RIGHT, 375);
//       // delay(200);
//       // leftStickPress(STICK_LEFT, 375);
//       // delay(200);
//       Serial0.write("6C");
//     }
//     else if (step == '7'){
//       Serial0.write("Starting Battle");
//       delay(1500);
//       Serial0.write("Starting Shiny Check");
//       delay(2000);
//       Serial0.write("Screenshotting");
//       delay(2000);
//       Serial0.write("Ending Shiny Check");
//       delay(1500); 
//       Serial0.write("Ending Scripted Input");
//     }
// }

// void arceus_reset(char step) {
//   if (step == '3') {
//           //after load
//           //dpad up
//           //wait 14
//           Serial0.write("Ending Darkness Check");
//           delay(1000); //Wait for game to fully load
//           dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME);
//           delay(13000);//cutscene
//           buttonPress(NSButton_A, PRESS_TIME);
//           // wait 10-12 (12 probably upper bound)
//           Serial0.write("Starting Battle");
//           delay(4500);
//           Serial0.write("Starting Shiny Check");
//           delay(3500);
//           Serial0.write("Screenshotting");
//           delay(6500);
//           Serial0.write("Ending Shiny Check");
//           delay(3000); //could almost certainly be faster by a few seconds (maybe 2) (cut 1.25 already) (cant cut more i dont think because of occasional breelom friendship action)
//           Serial0.write("Ending Scripted Input");
//           //shiny check
//         }
// }

// void darkrai_reset(char){
//   if (step == '3') {
//     Serial0.write("Ending Darkness Check");
//     delay(1000); //Wait for game to fully load
//     buttonPress(NSButton_A, PRESS_TIME);
//     delay(5500);//cutscene
//     Serial0.write("Starting Battle");
//     buttonPress(NSButton_A, PRESS_TIME);
//     delay(3000);
//     Serial0.write("Starting Shiny Check");
//     delay(6000);
//     Serial0.write("Screenshotting");
//     delay(3000);
//     Serial0.write("Ending Shiny Check");
//     delay(1500); //could almost certainly be faster by a few seconds (maybe 2) (cut 1.25 already) (cant cut more i dont think because of occasional breelom friendship action)
//     Serial0.write("Ending Scripted Input");
//   }
// }
void bdsp_premier_balls() {
  //should be at pokemart hovering the poke ball purchase option
  Serial0.write("Buying 50 Premier balls");
  int count = 0;

  while (count < 50)
  {
    Serial0.write("Buying ball ");
    Serial0.write(String(count).c_str());
    delay(1000); //Wait 

    delay(1000); //Wait more
    buttonPress(NSButton_A, PRESS_TIME); 
    delay(300);
    dPadPress(NSGAMEPAD_DPAD_UP, 1750);
    delay(300);

    buttonPress(NSButton_A, PRESS_TIME); 
    delay(1250);

    buttonPress(NSButton_A, PRESS_TIME); 
    delay(1000);
    buttonPress(NSButton_A, PRESS_TIME); 
    delay(1000);
    buttonPress(NSButton_A, PRESS_TIME); 
    delay(1000);
    buttonPress(NSButton_A, PRESS_TIME); 
    count = count + 1;
  }
  Serial0.write("Done");
}

void bdsp_reset(char step) {
  //in battle -> close game -> start game
  if (step == '1'){//Close Game, extra rest to try to prevent errors
    Serial0.write("Resetting");
    buttonPress(NSButton_Home, PRESS_TIME);
    // delay(500);
    delay(625);
    buttonPress(NSButton_X, PRESS_TIME);
    // delay(500);
    delay(625);
    buttonPress(NSButton_A, PRESS_TIME);
    Serial0.write("Starting Rest");
    delay(3000);//adding additional delay trying to prevent crashes
    Serial0.write("Stopping Rest");    
  }
  else if (step == '2') {
    delay(750);
    buttonPress(NSButton_A, PRESS_TIME);
    delay(750);
    buttonPress(NSButton_A, PRESS_TIME);
    delay(2000); //Waiting out the animation from the switch on game startup, excess time here is fine
    Serial0.write("Starting Darkness Check");
  }
  //start game -> palkia/dialga animation
  else if (step == '3') {
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
  else if (step == 'E'){
    buttonPress(NSButton_A, PRESS_TIME);
    delay(30000);
    Serial0.write("Error Resolved");
  }
}

void bdsp_rasmanas_park(uint16_t battle_start_ms) {
  Serial0.write("Ending Darkness Check");
  delay(1000); //Wait for game to fully load
  buttonPress(NSButton_A, PRESS_TIME); //talk
  Serial0.write("Starting Battle");
  // delay(500); 
  delay(650); //raised from 500 for rayquaza
  buttonPress(NSButton_A, PRESS_TIME); //remove dialogue box

  delay(battle_start_ms); 

  Serial0.write("Starting Shiny Check");
  delay(2000); 
  Serial0.write("Screenshotting");
  // delay(3000);
  delay(4000); //rayquaza
  Serial0.write("Ending Shiny Check");
  delay(1250); 
  Serial0.write("Ending Scripted Input");
}

//Upload thru COM8, unplug, plug USB port into Switch, plug COM8 in again.
//Unplug from switch to upload

void loop() {
  //cant send two messages in under 1000 ms or else it will stack bc of python reciever code.
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
      bdsp_reset('3');
    }
    else if (step == '4') {
      // bdsp_rasmanas_park(6500);
      bdsp_rasmanas_park(6000);//rayquaza
    }
    else if (step == '9'){

    }
    else if (step == 'E') {
      bdsp_reset('E');
    }
    else if (step == 'Z'){
      bdsp_premier_balls();
    }

    else if (step == 'A') { buttonPress(NSButton_A, PRESS_TIME); }
    else if (step == 'B') { buttonPress(NSButton_B, PRESS_TIME); }
    else if (step == 'X') { buttonPress(NSButton_X, PRESS_TIME); }
    else if (step == 'Y') { buttonPress(NSButton_Y, PRESS_TIME); }

    else if (step == 'U') { dPadPress(NSGAMEPAD_DPAD_UP, PRESS_TIME); }
    else if (step == 'D') { dPadPress(NSGAMEPAD_DPAD_DOWN, PRESS_TIME); }
    else if (step == 'L') { dPadPress(NSGAMEPAD_DPAD_LEFT, PRESS_TIME); }
    else if (step == 'R') { dPadPress(NSGAMEPAD_DPAD_RIGHT, PRESS_TIME); }

  }
}
