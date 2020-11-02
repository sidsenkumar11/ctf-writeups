#include <fstream>
#include <experimental/filesystem>
#include "Memory.hpp"

void Memory::load(std::string filename, address_t addr)
{
    std::ifstream fin(filename, std::ios::in | std::ios::binary);
    fin.read(((char *) memory) + addr, std::experimental::filesystem::file_size(filename));
    fin.close();
}

byte_t& Memory::operator[] (address_t addr)
{
    return memory[addr];
}

void Memory::set_word(address_t addr, word_t x)
{
    memory[addr] = x & 0xFF;
    memory[addr+1] = (x & 0xFF00) >> 8;
}

word_t Memory::get_word(address_t addr)
{
    return (memory[addr+1] << 8) | memory[addr];
}

void Memory::get_word(byte_t& high, byte_t& low, address_t addr)
{
    high = memory[addr + 1];
    low = memory[addr];
}
