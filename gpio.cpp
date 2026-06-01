#include "gpio.hpp"

gpio::gpio(int mode){
    state = mode;
    switch (state){
        case 4:
            pi = pigpio_start(NULL, NULL);
            //std::cout<<"Pi 4"<< std::endl;
            break;
        case 5:
            pi = lgGpiochipOpen(0);
            //std::cout<<"Pi 5"<< std::endl;
            break;
        default:
            std::cout<<"ERROR IN GPIO STATE"<<std::endl;
    }
    if (state < 0){
        std::cout<<"ERROR IN SETTING UP GPIO CONNECTION"<<std::endl;
    }
}

void gpio::setMode(int port, int IO){
    switch (state){
        case 4:
            set_mode(pi, port, IO);
            break;
        case 5:
            if (IO == 0){//input
                lgGpioClaimInput(pi, 0, port);
            }
            else{
                lgGpioClaimOutput(pi, 0, port, 1);
            }
    }
}

int gpio::read(int port){
    int val;
    switch(state){
        case 4:
            val = gpio_read(pi, port);
            break;
        case 5:
            val = lgGpioRead(pi, port);
            break;
        default:
            val = -1;
            break;
    }
    return val;
}