#include <iostream>
#include <pigpiod_if2.h>
#include <lgpio.h>

//just a wrapper cause the pi 4 and 5 use different libraries, makes switching between the two easier
class gpio{
    public:
        gpio(){gpio(4);}
        gpio(int);
        void setMode(int, int);
        int read(int);
    private:
        int state;
        int pi;
};