#include <Arduino.h>
#include "Cmd.h"
#include "Ticker.h"
#include "globals.h"



#define _2PI 6.283185307179586476925286766559
#define time_task_periond_in_ms 1
const static float d_timer = float(time_task_periond_in_ms/1000.0); 

void _timer_task(void){
    float tmp_t = (float) micros();  
    static float time_sec = 0;
   
   time_sec += d_timer; // in seconds

   float amplitude  =  globals[index("a1")].value;
   float frequency  =  globals[index("w1")].value; // Hz
   float offset     =  globals[index("a1")].value * 2;
    
    globals[index("f1")].value = offset + amplitude * sin(_2PI*frequency*time_sec); 
   

    amplitude  =  globals[index("a2")].value;
    frequency  =  globals[index("w2")].value; // Hz
    offset     =  globals[index("a2")].value * 2;

    globals[index("f2")].value = offset + amplitude * sin(_2PI*frequency*time_sec);

    tmp_t = (float) micros() - tmp_t ;
    if(tmp_t > globals[index("t")].value) globals[index("t")].value = tmp_t;

}



Ticker t = Ticker(_timer_task, time_task_periond_in_ms, 0, MILLIS);


void setup_fake_data() {
	globals[index("w1")].value = 0.01;
	globals[index("w2")].value = 0.03;
    globals[index("a1")].value = 2.0;
	globals[index("a2")].value = 3.0;

    randomSeed(127);
    
    /*
    cmdAdd("f1", [](int argcnt, char**){
        Stream *s = cmdGetStream();
        s->println(globals[index("f1")].value);
    });

    cmdAdd("f2", [](int argcnt, char**){
        Stream *s = cmdGetStream();
        s->println(globals[index("f2")].value);
    });
    */

    t.start();

}

void loop_fake_data() {
    t.update();
}   

