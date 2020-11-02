#pragma once
#include "chip9types.hpp"

class Memory {
    private:
        byte_t memory[1 << 16];
    public:
        virtual byte_t& operator[] (address_t addr);
        virtual void set_word(address_t addr, word_t x);
        virtual word_t get_word(address_t addr);
        virtual void get_word(byte_t& high, byte_t& low, address_t addr);
        virtual void load(std::string filename, address_t addr);
};
