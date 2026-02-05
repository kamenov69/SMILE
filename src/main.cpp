

/* v0.2

   main.cpp - Main loop for Arduino
   Part of SMILE project -

*/


#include <Arduino.h>
#include "board.h"
#include "globalVars.h"
//#include "data_faker.h"

static const char name_glo[] PROGMEM = "glo";


void setup() {
  setup_board();
  //setup_fake_data();

  
  //add_new_global_var_P((PGM_P) name_glo, 1, 0, 10);
  add_new_global_var("glo", 1, 0, 10);
   add_new_global_var("glo1", 1, 0, 10);
  setup_var_list_cmd();
}

void loop() {
  // put your main code here, to run repeatedly:
  loop_board();
  //loop_fake_data();
  

}

