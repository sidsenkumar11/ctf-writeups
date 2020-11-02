#include <iostream>
#include <SDL2/SDL.h>
#include "Emulator.hpp"

int main(int argc, char** argv) {
    Emulator *vm = new Emulator();
    vm->init();
    vm->run();
    return 0;
}
