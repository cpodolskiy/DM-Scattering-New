#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <iostream>
#include <stdio.h>
#include <string>
#include <cstdio>
#include <ctime>
#include <chrono>


struct reading{
    double position;
    double velocity;
    double timeStamp;
};


class writeMemory{
    

    public:
        writeMemory(bool commit);
        ~writeMemory();

        void write(reading);
        void log(std::string str);
        void clearLogs();
        double getStartingPos();

    private:
        static boost::interprocess::shared_memory_object shm_obj;
        static boost::interprocess::mapped_region region;
        static FILE* fptr;
        static const char* FILENAME;
        static bool commit;
        //std::chrono::_V2::system_clock::time_point start;
};


class readMemory{
    public:
        readMemory(bool read);
        reading read();
    private:
        static boost::interprocess::shared_memory_object shm_obj;
        static boost::interprocess::mapped_region region;
        static FILE* fptr;
        static const char* FILENAME;
        static bool commit;
};

