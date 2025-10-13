

/* v0.1 

   main.cpp - Main loop for Arduino
   Part of SMILE project -

*/


#include <Arduino.h>
#include "board.h"
#include "globals.h"
#include "data_faker.h"

void setup() {
  setup_board();

  setup_globals();

  setup_fake_data();
}

void loop() {
  // put your main code here, to run repeatedly:
  loop_board();
  loop_fake_data();
  

}

