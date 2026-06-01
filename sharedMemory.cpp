#include "sharedMemory.hpp"


writeMemory::writeMemory(const bool write){
    shm_obj = boost::interprocess::shared_memory_object(boost::interprocess::open_or_create, "reading", boost::interprocess::read_write);
    shm_obj.truncate(24);
    region = boost::interprocess::mapped_region(shm_obj, boost::interprocess::read_write);
    commit = write;
    //start = std::chrono::high_resolution_clock::now();
}

writeMemory::~writeMemory(){
    //boost::interprocess::shared_memory_object::remove("reading");
    fptr = fopen(FILENAME, "a");
    fprintf(fptr, "Tried to DELETED MEMORY, did not actually");
    fclose(fptr);
}

void writeMemory::write(reading value){
    // reading* ptr;
    // ptr = static_cast<reading*>(region.get_address());
    // *ptr = value;
    *static_cast<reading*>(region.get_address()) = value;
    if (commit){
        fptr = fopen(FILENAME, "a");
        //fprintf(fptr, "Wrote: %f %f\n", value.position, value.velocity);
        auto now = std::chrono::duration_cast<std::chrono::duration<double>>(std::chrono::high_resolution_clock::now().time_since_epoch()).count();
        fprintf(fptr,"%f,%f,%f\n",now,value.position,value.velocity);
        fclose(fptr);
    }
    
}

void writeMemory::log(std::string str){
    fptr = fopen(FILENAME, "a");
    const char* cstring = str.c_str();
    fprintf(fptr, "\nLOGGED: %s\n", cstring);
    fclose(fptr);

}

void writeMemory::clearLogs(){
    std::remove("Logging.txt");
    fptr = fopen("Logging.txt", "a");
    if (fptr == NULL){
        std::cout<<"ERROR IN OPENING LOGS"<<std::endl;
    }
    fprintf(fptr, "---CLEARED LOGS---");
    fclose(fptr);
}


boost::interprocess::shared_memory_object writeMemory::shm_obj;
boost::interprocess::mapped_region writeMemory::region;
FILE* writeMemory::fptr;
const char* writeMemory::FILENAME = "Logging.csv";
bool writeMemory::commit;
//std::chrono::_V2::system_clock::time_point start;

readMemory::readMemory(bool read){
    while (true){
        try{
    shm_obj = boost::interprocess::shared_memory_object(boost::interprocess::open_only, "reading", boost::interprocess::read_only);
    region = boost::interprocess::mapped_region(shm_obj, boost::interprocess::read_only);
    commit = read;
    break;
        }catch(boost::interprocess::interprocess_exception &e){
            std::cout<<e.what()<<std::endl;
        }
    }
}


reading readMemory::read(){ 
    reading val = *static_cast<reading*>(region.get_address());
    if (commit){
        fptr = fopen(FILENAME, "a");
        fprintf(fptr, "Read: %f %f\n", val.position, val.velocity);
        fclose(fptr);
    }
    return val;
}

boost::interprocess::shared_memory_object readMemory::shm_obj;
boost::interprocess::mapped_region readMemory::region;
FILE* readMemory::fptr;
const char* readMemory::FILENAME = "Logging.txt";
bool readMemory::commit;