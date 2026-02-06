

/* v0.2

   main.cpp - Main loop for Arduino
   Part of SMILE project -

*/


#include <Arduino.h>
#include "board.h"
#include "globalVars.h"

#include "ps_data.h"


void setup() {
  setup_board();
  setup_ps_data();

  add_new_global_var("glo", 1, 0, 10);
  add_new_global_var("glo1", 7, 10, 10);
  setup_var_list_cmd();
}

void loop() {
  
  loop_board();
  loop_ps_data();

}

