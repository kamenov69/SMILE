#include <Arduino.h>
#include "Cmd.h"
#include "Ticker.h"

#include "globalVars.h"



#define _2PI 6.283185307179586476925286766559
#define time_task_periond_in_ms 1
const static float d_timer = float(time_task_periond_in_ms/1000.0); 

float amplitude;
float frequency; // Hz
float offset ;

float calck_sin(void){
    static float time_sec = 0;
    time_sec += d_timer; // in seconds
    return offset + amplitude * sin(_2PI*frequency*time_sec);
}

void _timer_task(void){
   unsigned long task_tmr = micros();

   amplitude  =  globals.get("a1");
   frequency  =  globals.get("w1"); // Hz
   offset     =  globals.get("a1")*2.0;
    
   globals.set("f1", calck_sin()); 

   amplitude  =  globals.get("a2");
   frequency  =  globals.get("w2"); // Hz
   offset     =  globals.get("a2")*2.0;
   
   globals.set("f2", calck_sin());
   task_tmr = micros()  - task_tmr;
   if(globals.get("t") < (float)task_tmr)  globals.set("t", (float)task_tmr);

}



Ticker t = Ticker(_timer_task, time_task_periond_in_ms, 0, MILLIS);


void setup_ps_data() {

    add_new_global_var("w1", 0.1, 0.01, 10000.0);
    add_new_global_var("w2", 0.1, 0.01, 10000.0);
    add_new_global_var("a1", 3.1, 0.0, 10.0);
    add_new_global_var("a2", 3.1, 0.0, 10.0);
    add_new_global_var("f1", 0.1, 0.0, 0.0); // read only member 
    add_new_global_var("f2", 0.1, 0.0, 0.0); // read only 
    add_new_global_var("t", 0, 0, 0);

    t.start();

}

void loop_ps_data() {
    t.update();
}   

