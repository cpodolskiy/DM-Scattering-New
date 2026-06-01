#include <pigpiod_if2.h>
#include <iostream>
#include "sharedMemory.hpp"
#include <chrono>
#include <fstream>
#include <iomanip>
#include "gpio.hpp"
//#include <Python.h>

using namespace std;

class encoder{
    public:
        encoder(){gpio gp(4);encoder(-1, -1, 'S', gp);}
        encoder(int port1, int port2, char state, gpio &GPIO){
            portA = port1; portB = port2; this->state = state; this->GPIO = GPIO;
            initialize();
            //mem.log("finished initializing");
        }

        ~encoder(){
            //mem.log("ENCODER CALLED DECONSTRUCTOR");
            mem.~writeMemory();
            run = false;
        }
        
        void begin(){
            run = true;
            dir = 1;

            if (state == 'R'){
            // portAPast = gpio_read(pi, portA);
            // portBPast = gpio_read(pi, portB);
            portAPast = GPIO.read(portA);
            portBPast = GPIO.read(portB);
            while (run){
                
                // portAVal = gpio_read(pi, portA);
                // portBVal = gpio_read(pi, portB);

                portAVal = GPIO.read(portA);
                portBVal = GPIO.read(portB);
                
                if (double(chrono::duration_cast<chrono::duration<double>>(chrono::high_resolution_clock::now() - t1).count()) > 0.1){//adjust tollerance
                //if (temp > 0.1){ //|| nearZeroFrequency){
                    frequency = 0;
                    output.velocity = frequency;
                    mem.write(output);
                    nearZeroFrequency = true;
                    //t2 = chrono::high_resolution_clock::now();
                }
                // }else{
                //     temp = chrono::duration_cast<chrono::duration<double>>(chrono::high_resolution_clock::now() - t1).count();
                // }

                if ((portAVal != portAPast) || (portBVal != portBPast)){
                    t1 = chrono::high_resolution_clock::now();

                    dir = !(portAPast ^ portBVal);
                    position.d_val += dir? countPerEdge : -1 * countPerEdge;
                    if (!((position.u_val ^ wrappingMask) & wrappingMask)){
                        position.d_val -= 1;
                    }
                    if (position.u_val & signbit){position.d_val += 1;}
                    
                    //if ((pastPosition.u_val & mask) != (position.u_val & mask)){//will only have an effect when acconting for gear ratio
                        frequency = double(chrono::duration_cast<chrono::duration<double, micro>>(t1 - t2).count() * 0.000004);
                        frequency =  1.0 / frequency;
                        frequency = frequency / 12.0;
                        frequency = frequency / 377.9330;
                        output.position = position.d_val;
                        pastFrequencies[increment] = frequency;
                        if (frequency > 0.15 || frequency < -0.15){
                            frequency = pastFrequencies[5];
                        }else if (increment >= 4){
                            frequency = 0;
                            for (int i = 0; i <= 4; i ++){
                                frequency += pastFrequencies[i];
                            }
                            frequency /= 5;
                            pastFrequencies[5] = frequency;
                            increment = 0;
                        }else{
                            pastFrequencies[increment++] = frequency;
                            frequency = pastFrequencies[5];
                        }
                        output.velocity = frequency;
                        //output.velocity = (position.d_val - pastPosition.u_val) / (chrono::duration_cast<chrono::duration<double>>(t1 - t2).count());
                        mem.write(output);
                        //cout<<'v'<<output.velocity<<endl;
                        //cout<<'p'<<output.position<<endl;
                        pastPosition.d_val = position.d_val;
                        t2 = t1;
                        //nearZeroFrequency = false;
                    //}else{
                    //     mem.log("NOT WROTE: "+to_string(position.d_val));
                    // }
                }
                portAPast = portAVal;
                portBPast = portBVal;
            }
            }else if (state == 'S'){
                while (run){
                if (true){
                    test.d_val += sim_increment;
                    if ((test.u_val & mask) != (pastTest.u_val & mask)){
                        try{
                            output.position = test.d_val;
                            output.velocity = test.u_val;
                            //mem.write(output);
                            //cout<<'p'<<test.d_val<<endl;
                            //cout<<'v'<<test.u_val<<endl;
                        }catch(const exception &e){
                            //mem.log(e.what());
                        }
                    }
                    else{
                        //mem.log("NOT WROTE "+std::to_string(test.d_val)+" WITH "+std::to_string(test.u_val));
                    }
                    pastTest.u_val = test.u_val;
                }
            }
            }
        }
        double getPosition(){
            return output.position;
        }
        double getVelocity(){
            return output.velocity;
        }
    private:
        void initialize(){
            position.d_val = pastPosition.d_val = 0;
            t1 = chrono::high_resolution_clock::now();
            t2 = chrono::high_resolution_clock::now();
            output.position = position.d_val;
            output.velocity = 0;
            mem.write(output);
            
            switch(state){
                case 'R':{
                    //mem.clearLogs();
                    //mem.log("---REAL---");
                    // set_mode(pi, portA, PI_INPUT);
                    // set_mode(pi, portB, PI_INPUT);
                    // set_mode(pi, 1, PI_OUTPUT);
                    //mem.log("PortA: "+to_string(portA));
                    //mem.log("PortB: "+to_string(portB));
                    // gpio_write(pi, 1, 1);
                    GPIO.setMode(portA, PI_INPUT);
                    GPIO.setMode(portB, PI_INPUT);
                    break;
                }
                case 'S':
                    //mem.clearLogs();
                    //mem.log("---SIM---");
                    test.u_val = 0;
                    pastTest.u_val = 0;
                    //mem.log("SIM PortA: "+to_string(portA));
                    //mem.log("SIM PortB: "+to_string(portB));
                    break;
                default:
                    //mem.log("---ERROR-IN-STATE---");
                    break;
            }
        }

        writeMemory mem = writeMemory(false);
        
        bool nearZeroFrequency = false;
        double temp = 0;

        char state;// either R or S, Real or Sim
        gpio GPIO;

        int portA;
        int portB;

        int portAVal;
        int portBVal;
        int dir;
        int portAPast;
        int portBPast;

        union pos {//stupidest data structure ever
            double d_val;
            uint64_t u_val;
        };
        union pos position;
        union pos pastPosition;
        reading output;
        reading sim_output;
        bool run;

        double frequency;
        chrono::high_resolution_clock::time_point t1;
        chrono::high_resolution_clock::time_point t2;
        int increment = 0;
        double pastFrequencies[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        
        uint64_t mask = 0xFFFFFFFF00000000;
        uint64_t sim_increment = 0x0000000000000001;
        uint64_t wrappingMask = 0x3FF0000000000000;
        uint64_t signbit = 0x8000000000000000;

        union pos test;
        union pos pastTest;

        const double countPerEdge = 1/(48 * 377.933); //48 edges per rotation, gear ratio of 377.933 : 1 
        //const double countPerEdge = 0.020833333;//without gear ratio, for testing only
};





extern "C"{

// static PyObject *method_readPosition(PyObject *self, PyObject *args) {
//     readMemory readMem(false);
//     double data = readMem.read().position;
//     return PyFloat_FromDouble(data);
// }

// static PyObject *method_readVelocity(PyObject *self, PyObject *args){
//     readMemory readMem(false);
//     double data = readMem.read().position;
//     return PyFloat_FromDouble(data);
// }
double readPosition(){
    readMemory readMem(false);
    double data = readMem.read().position;
    return data;
    
}
double readVelocity(){
    readMemory readMem(false);
    double data = readMem.read().velocity;
    return data;
}
}

//takes args pinA, pinB, r/s (real or sim), and 4/5 (pi version)
int main(int argc, const char* argv[]){
    //int pi = pigpio_start(NULL, NULL);
    gpio GPIO(std::atoi(argv[4]));
    if (argc < 5){
        cout<<"ERROR TOO FEW ARGS"<<endl;
        return 1;
    }
    // if (pi < 0){
    //     cout<<"ERROR GPIO FAILED TO INITIALIZE"<<endl;
    //     return 1;
    // };

    encoder en(std::atoi(argv[1]), std::atoi(argv[2]), static_cast<char>(*argv[3]), GPIO);
    en.begin();
    return 0;
}