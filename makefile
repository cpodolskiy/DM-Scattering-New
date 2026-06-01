Encoder: Encoder.cpp sharedMemory.cpp gpio.cpp
# 	sudo g++ -Wall -pthread -o Encoder Encoder.cpp  sharedMemory.cpp -lpigpiod_if2 -lrt -Ofast
# 	sudo g++ -Wall -pthread -shared -fPIC -o Encoder.so Encoder.cpp sharedMemory.cpp -lpigpiod_if2 -lrt -Ofast
# 	sudo g++ -Wall -c gpio.cpp -o gpio.o -Ofast
# 	sudo g++ -Wall -c sharedMemory.cpp -o sharedMemory.o -Ofast
# 	sudo g++ -Wall -c -pthread Encoder.cpp -o Encoder.o -llgpio -lpigpiod_if2 -lrt -Ofast
# 	sudo g++ -Wall Encoder.o sharedMemory.o gpio.o -o Encoder
	sudo g++ -Wall -pthread -o Encoder Encoder.cpp sharedMemory.cpp gpio.cpp -lpigpiod_if2 -lrt -llgpio -Ofast
	sudo g++ -Wall -pthread -shared -fPIC -o Encoder.so Encoder.cpp sharedMemory.cpp gpio.cpp -lpigpiod_if2 -lrt -llgpio -Ofast
	
clean:
	rm -f *.o output
	rm -f *.so output
