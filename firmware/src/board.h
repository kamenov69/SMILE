#ifndef __BOARD_H
#define __BOARD_H

#define __NAME "SMILE_Arduino"
#include <Arduino.h>

// --- Pins Deffinitions 

#define LED       LED_BUILTIN
#define APIN_MAX  4

// --- Operation modes
#define MIN_MODE 0
#define MAX_MODE 3


#define LED_PERIOD 250  // ms



extern uint8_t mode;
void setup_board();
void loop_board();

#endif