#include "RegisterFile.hpp"

word_t RegisterFile::BC()
{
    return ((registers[B]) << 8) | registers[C];
}

word_t RegisterFile::DE()
{
    return ((registers[D]) << 8) | registers[E];
}

word_t RegisterFile::HL()
{
    return ((registers[H]) << 8) | registers[L];
}

void RegisterFile::set_BC(word_t val)
{
    registers[B] = (val & 0xFF00) >> 8;
    registers[C] = val & 0xFF;
}

void RegisterFile::set_DE(word_t val)
{
    registers[D] = (val & 0xFF00) >> 8;
    registers[E] = val & 0xFF;
}

void RegisterFile::set_HL(word_t val)
{
    registers[H] = (val & 0xFF00) >> 8;
    registers[L] = val & 0xFF;
}

int RegisterFile::ZFLAG()
{
    return (this->flags & 0b10000000) >> 7;
}

int RegisterFile::NFLAG()
{
    return (this->flags & 0b01000000) >> 6;
}

int RegisterFile::HFLAG()
{
    return (this->flags & 0b00100000) >> 5;
}

int RegisterFile::CFLAG()
{
    return (this->flags & 0b00010000) >> 5;
}

void RegisterFile::set_ZFLAG(bool set)
{
    if(set)
    {
        this->flags = flags | (1 << 7);
    }
    else
    {
        this->flags = flags & 0b01111111;
    }
}

void RegisterFile::set_NFLAG(bool set)
{
    if(set)
    {
        this->flags = flags | (1 << 6);
    }
    else
    {
        this->flags = flags & 0b10111111;
    }
}

void RegisterFile::set_HFLAG(bool set)
{
    if(set)
    {
        this->flags = flags | (1 << 5);
    }
    else
    {
        this->flags = flags & 0b11011111;
    }
}

void RegisterFile::set_CFLAG(bool set)
{
    if(set)
    {
        this->flags = flags | (1 << 4);
    }
    else
    {
        this->flags = flags & 0b11101111;
    }
}
