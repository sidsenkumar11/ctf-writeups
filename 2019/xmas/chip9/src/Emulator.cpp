#include <iostream>
#include <sstream>
#include "Emulator.hpp"
#include "Memory.hpp"

#define BREAKPOINT_ADDR 690

#define DEBUG \
    if (pc >= BREAKPOINT_ADDR) { \
        std::cout << "A:     0x" << std::hex << unsigned(regs[A]) << std::endl; \
        std::cout << "B:     0x" << std::hex << unsigned(regs[B]) << std::endl; \
        std::cout << "C:     0x" << std::hex << unsigned(regs[C]) << std::endl; \
        std::cout << "D:     0x" << std::hex << unsigned(regs[D]) << std::endl; \
        std::cout << "E:     0x" << std::hex << unsigned(regs[E]) << std::endl; \
        std::cout << "H:     0x" << std::hex << unsigned(regs[H]) << std::endl; \
        std::cout << "L:     0x" << std::hex << unsigned(regs[L]) << std::endl; \
        std::cout << "BC:    0x" << std::hex << unsigned(regs.BC()) << std::endl; \
        std::cout << "DE:    0x" << std::hex << unsigned(regs.DE()) << std::endl; \
        std::cout << "HL:    0x" << std::hex << unsigned(regs.HL()) << std::endl; \
        std::cout << "(HL):  0x" << std::hex << unsigned(mem[regs.HL()]) << std::endl; \
        std::cout << "SP:    0x" << std::hex << unsigned(sp) << std::endl; \
        std::cout << "PC:    0x" << std::hex << unsigned(pc) << std::endl; \
        std::cout << "FLAGS: " << (regs.ZFLAG() ? "Z " : "  ") << (regs.NFLAG() ? "N " : "  ") << (regs.HFLAG() ? "H " : "  ") << (regs.CFLAG() ? "C " : "  ") <<  std::endl; \
        std::cout << "\n" << inst_repr() << std::endl; \
        std::cout << "===================================================" << std::endl; \
        getchar(); \
    }

void Emulator::init()
{
    this->screen = new Screen<64, 128>("CHIP-9 Emulator");
    this->mem.load("bootrom", 0x0000);
    this->mem.load("rom", 0x0597);
    pc = 0x0000;
}

void Emulator::run()
{
    int8_t sres8;
    uint8_t res8;
    uint16_t res16;
    uint16_t dstVal;

    for (int i = 0; i <= 0xFF; i++)
    {
        jumptable[i] = &&UNKNOWN_OP;
        names[i] = "UNKNOWN INST";
    }

    jumptable[0x20] = &&LDIB;
    jumptable[0x30] = &&LDIC;
    jumptable[0x40] = &&LDID;
    jumptable[0x50] = &&LDIE;
    jumptable[0x60] = &&LDIH;
    jumptable[0x70] = &&LDIL;
    jumptable[0x80] = &&LDIMHL;
    jumptable[0x90] = &&LDIA;
    jumptable[0x21] = &&LDXBC;
    jumptable[0x31] = &&LDXDE;
    jumptable[0x41] = &&LDXHL;
    jumptable[0x22] = &&LDXSP;
    jumptable[0x81] = &&PUSHB;
    jumptable[0x91] = &&PUSHC;
    jumptable[0xA1] = &&PUSHD;
    jumptable[0xB1] = &&PUSHE;
    jumptable[0xC1] = &&PUSHH;
    jumptable[0xD1] = &&PUSHL;
    jumptable[0xC0] = &&PUSHMHL;
    jumptable[0xD0] = &&PUSHA;
    jumptable[0x51] = &&PUSHBC;
    jumptable[0x61] = &&PUSHDE;
    jumptable[0x71] = &&PUSHHL;
    jumptable[0x82] = &&POPB;
    jumptable[0x92] = &&POPC;
    jumptable[0xA2] = &&POPD;
    jumptable[0xB2] = &&POPE;
    jumptable[0xC2] = &&POPH;
    jumptable[0xD2] = &&POPL;
    jumptable[0xC3] = &&POPMHL;
    jumptable[0xD3] = &&POPA;
    jumptable[0x52] = &&POPBC;
    jumptable[0x62] = &&POPDE;
    jumptable[0x72] = &&POPHL;
    jumptable[0x09] = &&MOVBB;
    jumptable[0x19] = &&MOVBC;
    jumptable[0x29] = &&MOVBD;
    jumptable[0x39] = &&MOVBE;
    jumptable[0x49] = &&MOVBH;
    jumptable[0x59] = &&MOVBL;
    jumptable[0x69] = &&MOVBMHL;
    jumptable[0x79] = &&MOVBA;
    jumptable[0x89] = &&MOVCB;
    jumptable[0x99] = &&MOVCC;
    jumptable[0xA9] = &&MOVCD;
    jumptable[0xB9] = &&MOVCE;
    jumptable[0xC9] = &&MOVCH;
    jumptable[0xD9] = &&MOVCL;
    jumptable[0xE9] = &&MOVCMHL;
    jumptable[0xF9] = &&MOVCA;
    jumptable[0x0A] = &&MOVDB;
    jumptable[0x1A] = &&MOVDC;
    jumptable[0x2A] = &&MOVDD;
    jumptable[0x3A] = &&MOVDE;
    jumptable[0x4A] = &&MOVDH;
    jumptable[0x5A] = &&MOVDL;
    jumptable[0x6A] = &&MOVDMHL;
    jumptable[0x7A] = &&MOVDA;
    jumptable[0x8A] = &&MOVEB;
    jumptable[0x9A] = &&MOVEC;
    jumptable[0xAA] = &&MOVED;
    jumptable[0xBA] = &&MOVEE;
    jumptable[0xCA] = &&MOVEH;
    jumptable[0xDA] = &&MOVEL;
    jumptable[0xEA] = &&MOVEMHL;
    jumptable[0xFA] = &&MOVEA;
    jumptable[0x0B] = &&MOVHB;
    jumptable[0x1B] = &&MOVHC;
    jumptable[0x2B] = &&MOVHD;
    jumptable[0x3B] = &&MOVHE;
    jumptable[0x4B] = &&MOVHH;
    jumptable[0x5B] = &&MOVHL;
    jumptable[0x6B] = &&MOVHMHL;
    jumptable[0x7B] = &&MOVHA;
    jumptable[0x8B] = &&MOVLB;
    jumptable[0x9B] = &&MOVLC;
    jumptable[0xAB] = &&MOVLD;
    jumptable[0xBB] = &&MOVLE;
    jumptable[0xCB] = &&MOVLH;
    jumptable[0xDB] = &&MOVLL;
    jumptable[0xEB] = &&MOVLMHL;
    jumptable[0xFB] = &&MOVLA;
    jumptable[0x0C] = &&MOVMHLB;
    jumptable[0x1C] = &&MOVMHLC;
    jumptable[0x2C] = &&MOVMHLD;
    jumptable[0x3C] = &&MOVMHLE;
    jumptable[0x4C] = &&MOVMHLH;
    jumptable[0x5C] = &&MOVMHLL;
    jumptable[0x7C] = &&MOVMHLA;
    jumptable[0x8C] = &&MOVAB;
    jumptable[0x9C] = &&MOVAC;
    jumptable[0xAC] = &&MOVAD;
    jumptable[0xBC] = &&MOVAE;
    jumptable[0xCC] = &&MOVAH;
    jumptable[0xDC] = &&MOVAL;
    jumptable[0xEC] = &&MOVAMHL;
    jumptable[0xFC] = &&MOVAA;
    jumptable[0xED] = &&MOVHLBC;
    jumptable[0xFD] = &&MOVHLDE;
    jumptable[0x08] = &&CLRFLAG;
    jumptable[0x18] = &&SETFLAGZ1;
    jumptable[0x28] = &&SETFLAGZ0;
    jumptable[0x38] = &&SETFLAGN1;
    jumptable[0x48] = &&SETFLAGN0;
    jumptable[0x58] = &&SETFLAGH1;
    jumptable[0x68] = &&SETFLAGH0;
    jumptable[0x78] = &&SETFLAGC1;
    jumptable[0x88] = &&SETFLAGC0;
    jumptable[0x04] = &&ADDB;
    jumptable[0x14] = &&ADDC;
    jumptable[0x24] = &&ADDD;
    jumptable[0x34] = &&ADDE;
    jumptable[0x44] = &&ADDH;
    jumptable[0x54] = &&ADDL;
    jumptable[0x64] = &&ADDMHL;
    jumptable[0x74] = &&ADDA;
    jumptable[0xA7] = &&ADDI;
    jumptable[0x83] = &&ADDBC;
    jumptable[0x93] = &&ADDDE;
    jumptable[0xA3] = &&ADDHL;
    jumptable[0x84] = &&SUBB;
    jumptable[0x94] = &&SUBC;
    jumptable[0xA4] = &&SUBD;
    jumptable[0xB4] = &&SUBE;
    jumptable[0xC4] = &&SUBH;
    jumptable[0xD4] = &&SUBL;
    jumptable[0xE4] = &&SUBMHL;
    jumptable[0xF4] = &&SUBA;
    jumptable[0xB7] = &&SUBI;
    jumptable[0x03] = &&INCB;
    jumptable[0x13] = &&INCC;
    jumptable[0x23] = &&INCD;
    jumptable[0x33] = &&INCE;
    jumptable[0x43] = &&INCH;
    jumptable[0x53] = &&INCL;
    jumptable[0x63] = &&INCMHL;
    jumptable[0x73] = &&INCA;
    jumptable[0xA8] = &&INCBC;
    jumptable[0xB8] = &&INCDE;
    jumptable[0xC8] = &&INCHL;
    jumptable[0x07] = &&DECB;
    jumptable[0x17] = &&DECC;
    jumptable[0x27] = &&DECD;
    jumptable[0x37] = &&DECE;
    jumptable[0x47] = &&DECH;
    jumptable[0x57] = &&DECL;
    jumptable[0x67] = &&DECMHL;
    jumptable[0x77] = &&DECA;
    jumptable[0x05] = &&ANDB;
    jumptable[0x15] = &&ANDC;
    jumptable[0x25] = &&ANDD;
    jumptable[0x35] = &&ANDE;
    jumptable[0x45] = &&ANDH;
    jumptable[0x55] = &&ANDL;
    jumptable[0x65] = &&ANDMHL;
    jumptable[0x75] = &&ANDA;
    jumptable[0xC7] = &&ANDI;
    jumptable[0x85] = &&ORB;
    jumptable[0x95] = &&ORC;
    jumptable[0xA5] = &&ORD;
    jumptable[0xB5] = &&ORE;
    jumptable[0xC5] = &&ORH;
    jumptable[0xD5] = &&ORL;
    jumptable[0xE5] = &&ORMHL;
    jumptable[0xF5] = &&ORA;
    jumptable[0xD7] = &&ORI;
    jumptable[0x06] = &&XORB;
    jumptable[0x16] = &&XORC;
    jumptable[0x26] = &&XORD;
    jumptable[0x36] = &&XORE;
    jumptable[0x46] = &&XORH;
    jumptable[0x56] = &&XORL;
    jumptable[0x66] = &&XORMHL;
    jumptable[0x76] = &&XORA;
    jumptable[0xE7] = &&XORI;
    jumptable[0x86] = &&CMPB;
    jumptable[0x96] = &&CMPC;
    jumptable[0xA6] = &&CMPD;
    jumptable[0xB6] = &&CMPE;
    jumptable[0xC6] = &&CMPH;
    jumptable[0xD6] = &&CMPL;
    jumptable[0xE6] = &&CMPMHL;
    jumptable[0xF6] = &&CMPA;
    jumptable[0xF7] = &&CMPI;
    jumptable[0x0D] = &&CMPSB;
    jumptable[0x1D] = &&CMPSC;
    jumptable[0x2D] = &&CMPSD;
    jumptable[0x3D] = &&CMPSE;
    jumptable[0x4D] = &&CMPSH;
    jumptable[0x5D] = &&CMPSL;
    jumptable[0x6D] = &&CMPSMHL;
    jumptable[0x7D] = &&CMPSA;
    jumptable[0xE0] = &&SIN;
    jumptable[0xE1] = &&SOUT;
    jumptable[0xF0] = &&CLRSCR;
    jumptable[0xF1] = &&DRAW;
    jumptable[0x0F] = &&JMP;
    jumptable[0x1F] = &&JMPZ;
    jumptable[0x2F] = &&JMPNZ;
    jumptable[0x3F] = &&JMPN;
    jumptable[0x4F] = &&JMPNN;
    jumptable[0x5F] = &&JMPH;
    jumptable[0x6F] = &&JMPNH;
    jumptable[0x7F] = &&JMPC;
    jumptable[0x8F] = &&JMPNC;
    jumptable[0x9F] = &&JMPXX;
    jumptable[0xAF] = &&JMPXXZ;
    jumptable[0xBF] = &&JMPXXNZ;
    jumptable[0xCF] = &&JMPXXN;
    jumptable[0xDF] = &&JMPXXNN;
    jumptable[0xEF] = &&JMPXXH;
    jumptable[0xFF] = &&JMPXXNH;
    jumptable[0xEE] = &&JMPXXC;
    jumptable[0xFE] = &&JMPXXNC;
    jumptable[0x1E] = &&CALL;
    jumptable[0x0E] = &&RET;
    jumptable[0x00] = &&NOP;
    jumptable[0x6C] = &&HCF;

    names[0x20] = "LDI B";
    names[0x30] = "LDI C";
    names[0x40] = "LDI D";
    names[0x50] = "LDI E";
    names[0x60] = "LDI H";
    names[0x70] = "LDI L";
    names[0x80] = "LDI (HL)";
    names[0x90] = "LDI A";
    names[0x21] = "LDX BC";
    names[0x31] = "LDX DE";
    names[0x41] = "LDX HL";
    names[0x22] = "LDX SP";
    names[0x81] = "PUSH B";
    names[0x91] = "PUSH C";
    names[0xA1] = "PUSH D";
    names[0xB1] = "PUSH E";
    names[0xC1] = "PUSH H";
    names[0xD1] = "PUSH L";
    names[0xC0] = "PUSH (HL)";
    names[0xD0] = "PUSH A";
    names[0x51] = "PUSH BC";
    names[0x61] = "PUSH DE";
    names[0x71] = "PUSH HL";
    names[0x82] = "POP B";
    names[0x92] = "POP C";
    names[0xA2] = "POP D";
    names[0xB2] = "POP E";
    names[0xC2] = "POP H";
    names[0xD2] = "POP L";
    names[0xC3] = "POP (HL)";
    names[0xD3] = "POP A";
    names[0x52] = "POP BC";
    names[0x62] = "POP DE";
    names[0x72] = "POP HL";
    names[0x09] = "MOV B, B";
    names[0x19] = "MOV B, C";
    names[0x29] = "MOV B, D";
    names[0x39] = "MOV B, E";
    names[0x49] = "MOV B, H";
    names[0x59] = "MOV B, L";
    names[0x69] = "MOV B, (HL)";
    names[0x79] = "MOV B, A";
    names[0x89] = "MOV C, B";
    names[0x99] = "MOV C, C";
    names[0xA9] = "MOV C, D";
    names[0xB9] = "MOV C, E";
    names[0xC9] = "MOV C, H";
    names[0xD9] = "MOV C, L";
    names[0xE9] = "MOV C, (HL)";
    names[0xF9] = "MOV C, A";
    names[0x0A] = "MOV D, B";
    names[0x1A] = "MOV D, C";
    names[0x2A] = "MOV D, D";
    names[0x3A] = "MOV D, E";
    names[0x4A] = "MOV D, H";
    names[0x5A] = "MOV D, L";
    names[0x6A] = "MOV D, (HL)";
    names[0x7A] = "MOV D, A";
    names[0x8A] = "MOV E, B";
    names[0x9A] = "MOV E, C";
    names[0xAA] = "MOV E, D";
    names[0xBA] = "MOV E, E";
    names[0xCA] = "MOV E, H";
    names[0xDA] = "MOV E, L";
    names[0xEA] = "MOV E, (HL)";
    names[0xFA] = "MOV E, A";
    names[0x0B] = "MOV H, B";
    names[0x1B] = "MOV H, C";
    names[0x2B] = "MOV H, D";
    names[0x3B] = "MOV H, E";
    names[0x4B] = "MOV H, H";
    names[0x5B] = "MOV H, L";
    names[0x6B] = "MOV H, (HL)";
    names[0x7B] = "MOV H, A";
    names[0x8B] = "MOV L, B";
    names[0x9B] = "MOV L, C";
    names[0xAB] = "MOV L, D";
    names[0xBB] = "MOV L, E";
    names[0xCB] = "MOV L, H";
    names[0xDB] = "MOV L, L";
    names[0xEB] = "MOV L, (HL)";
    names[0xFB] = "MOV L, A";
    names[0x0C] = "MOV (HL), B";
    names[0x1C] = "MOV (HL), C";
    names[0x2C] = "MOV (HL), D";
    names[0x3C] = "MOV (HL), E";
    names[0x4C] = "MOV (HL), H";
    names[0x5C] = "MOV (HL), L";
    names[0x7C] = "MOV (HL), A";
    names[0x8C] = "MOV A, B";
    names[0x9C] = "MOV A, C";
    names[0xAC] = "MOV A, D";
    names[0xBC] = "MOV A, E";
    names[0xCC] = "MOV A, H";
    names[0xDC] = "MOV A, L";
    names[0xEC] = "MOV A, (HL)";
    names[0xFC] = "MOV A, A";
    names[0xED] = "MOV HL, BC";
    names[0xFD] = "MOV HL, DE";
    names[0x08] = "CLRFLAG";
    names[0x18] = "SETFLAG Z 1";
    names[0x28] = "SETFLAG Z 0";
    names[0x38] = "SETFLAG N 1";
    names[0x48] = "SETFLAG N 0";
    names[0x58] = "SETFLAG H 1";
    names[0x68] = "SETFLAG H 0";
    names[0x78] = "SETFLAG C 1";
    names[0x88] = "SETFLAG C 0";
    names[0x04] = "ADD B, A";
    names[0x14] = "ADD C, A";
    names[0x24] = "ADD D, A";
    names[0x34] = "ADD E, A";
    names[0x44] = "ADD H, A";
    names[0x54] = "ADD L, A";
    names[0x64] = "ADD (HL), A";
    names[0x74] = "ADD A, A";
    names[0xA7] = "ADDI A";
    names[0x83] = "ADD BC, A";
    names[0x93] = "ADD DE, A";
    names[0xA3] = "ADD HL, A";
    names[0x84] = "SUB B, A";
    names[0x94] = "SUB C, A";
    names[0xA4] = "SUB D, A";
    names[0xB4] = "SUB E, A";
    names[0xC4] = "SUB H, A";
    names[0xD4] = "SUB L, A";
    names[0xE4] = "SUB (HL), A";
    names[0xF4] = "SUB A, A";
    names[0xB7] = "SUBI A";
    names[0x03] = "INC B";
    names[0x13] = "INC C";
    names[0x23] = "INC D";
    names[0x33] = "INC E";
    names[0x43] = "INC H";
    names[0x53] = "INC L";
    names[0x63] = "INC (HL)";
    names[0x73] = "INC A";
    names[0xA8] = "INC BC";
    names[0xB8] = "INC DE";
    names[0xC8] = "INC HL";
    names[0x07] = "DEC B";
    names[0x17] = "DEC C";
    names[0x27] = "DEC D";
    names[0x37] = "DEC E";
    names[0x47] = "DEC H";
    names[0x57] = "DEC L";
    names[0x67] = "DEC (HL)";
    names[0x77] = "DEC A";
    names[0x05] = "AND B, A";
    names[0x15] = "AND C, A";
    names[0x25] = "AND D, A";
    names[0x35] = "AND E, A";
    names[0x45] = "AND H, A";
    names[0x55] = "AND L, A";
    names[0x65] = "AND (HL), A";
    names[0x75] = "AND A, A";
    names[0xC7] = "ANDI A";
    names[0x85] = "OR B, A";
    names[0x95] = "OR C, A";
    names[0xA5] = "OR D, A";
    names[0xB5] = "OR E, A";
    names[0xC5] = "OR H, A";
    names[0xD5] = "OR L, A";
    names[0xE5] = "OR (HL), A";
    names[0xF5] = "OR A, A";
    names[0xD7] = "ORI A";
    names[0x06] = "XOR B, A";
    names[0x16] = "XOR C, A";
    names[0x26] = "XOR D, A";
    names[0x36] = "XOR E, A";
    names[0x46] = "XOR H, A";
    names[0x56] = "XOR L, A";
    names[0x66] = "XOR (HL), A";
    names[0x76] = "XOR A, A";
    names[0xE7] = "XORI A";
    names[0x86] = "CMP B, A";
    names[0x96] = "CMP C, A";
    names[0xA6] = "CMP D, A";
    names[0xB6] = "CMP E, A";
    names[0xC6] = "CMP H, A";
    names[0xD6] = "CMP L, A";
    names[0xE6] = "CMP (HL), A";
    names[0xF6] = "CMP A, A";
    names[0xF7] = "CMPI A";
    names[0x0D] = "CMPS B, A";
    names[0x1D] = "CMPS C, A";
    names[0x2D] = "CMPS D, A";
    names[0x3D] = "CMPS E, A";
    names[0x4D] = "CMPS H, A";
    names[0x5D] = "CMPS L, A";
    names[0x6D] = "CMPS (HL), A";
    names[0x7D] = "CMPS A, A";
    names[0xE0] = "SIN";
    names[0xE1] = "SOUT";
    names[0xF0] = "CLRSCR";
    names[0xF1] = "DRAW";
    names[0x0F] = "JMP";
    names[0x1F] = "JMP Z";
    names[0x2F] = "JMP NZ";
    names[0x3F] = "JMP N";
    names[0x4F] = "JMP NN";
    names[0x5F] = "JMP H";
    names[0x6F] = "JMP NH";
    names[0x7F] = "JMP C";
    names[0x8F] = "JMP NC";
    names[0x9F] = "RELJMP";
    names[0xAF] = "RELJMP Z";
    names[0xBF] = "RELJMP NZ";
    names[0xCF] = "RELJMP N";
    names[0xDF] = "RELJMP NN";
    names[0xEF] = "RELJMP H";
    names[0xFF] = "RELJMP NH";
    names[0xEE] = "RELJMP C";
    names[0xFE] = "RELJMP NC";
    names[0x1E] = "CALL";
    names[0x0E] = "RET";
    names[0x00] = "NOP";
    names[0x6C] = "HCF";

    DISPATCH(0);
    while (1) {

        // ----------------------------------------
        // 2.1 Memory Operations
        // ----------------------------------------

        // 2.1.1 Loads

        LDIB:
            regs[B] = mem[pc+1];
            DISPATCH(2);

        LDIC:
            regs[C] = mem[pc+1];
            DISPATCH(2);

        LDID:
            regs[D] = mem[pc+1];
            DISPATCH(2);

        LDIE:
            regs[E] = mem[pc+1];
            DISPATCH(2);

        LDIH:
            regs[H] = mem[pc+1];
            DISPATCH(2);

        LDIL:
            regs[L] = mem[pc+1];
            DISPATCH(2);

        LDIMHL:
            mem[regs.HL()] = mem[pc+1];
            DISPATCH(2);

        LDIA:
            regs[A] = mem[pc+1];
            DISPATCH(2);

        LDXBC:
            mem.get_word(regs[B], regs[C], pc+1);
            DISPATCH(3);

        LDXDE:
            mem.get_word(regs[D], regs[E], pc+1);
            DISPATCH(3);

        LDXHL:
            mem.get_word(regs[H], regs[L], pc+1);
            DISPATCH(3);

        LDXSP:
            sp = mem.get_word(pc+1);
            DISPATCH(3);

        // 2.1.2 Stack pushes

        PUSHB:
            mem[sp] = regs[B];
            sp -= 2;
            DISPATCH(1);

        PUSHC:
            mem[sp] = regs[C];
            sp -= 2;
            DISPATCH(1);

        PUSHD:
            mem[sp] = regs[D];
            sp -= 2;
            DISPATCH(1);

        PUSHE:
            mem[sp] = regs[E];
            sp -= 2;
            DISPATCH(1);

        PUSHH:
            mem[sp] = regs[H];
            sp -= 2;
            DISPATCH(1);

        PUSHL:
            mem[sp] = regs[L];
            sp -= 2;
            DISPATCH(1);

        PUSHMHL:
            mem[sp] = mem[regs.HL()];
            sp -= 2;
            DISPATCH(1);

        PUSHA:
            mem[sp] = regs[A];
            sp -= 2;
            DISPATCH(1);

        PUSHBC:
            mem.set_word(sp, regs.BC());
            sp -= 2;
            DISPATCH(1);

        PUSHDE:
            mem.set_word(sp, regs.DE());
            sp -= 2;
            DISPATCH(1);

        PUSHHL:
            mem.set_word(sp, regs.HL());
            sp -= 2;
            DISPATCH(1);

        // 2.1.3 Stack pops

        POPB:
            sp += 2;
            regs[B] = mem[sp];
            DISPATCH(1);

        POPC:
            sp += 2;
            regs[C] = mem[sp];
            DISPATCH(1);

        POPD:
            sp += 2;
            regs[D] = mem[sp];
            DISPATCH(1);

        POPE:
            sp += 2;
            regs[E] = mem[sp];
            DISPATCH(1);

        POPH:
            sp += 2;
            regs[H] = mem[sp];
            DISPATCH(1);

        POPL:
            sp += 2;
            regs[L] = mem[sp];
            DISPATCH(1);

        POPMHL:
            sp += 2;
            mem[regs.HL()] = mem[sp];
            DISPATCH(1);

        POPA:
            sp += 2;
            regs[A] = mem[sp];
            DISPATCH(1);

        POPBC:
            sp += 2;
            mem.get_word(regs[B], regs[C], sp);
            DISPATCH(1);

        POPDE:
            sp += 2;
            mem.get_word(regs[D], regs[E], sp);
            DISPATCH(1);

        POPHL:
            sp += 2;
            mem.get_word(regs[H], regs[L], sp);
            DISPATCH(1);

        // 2.1.4 Register Movement

        MOVBB:
            regs[B] = regs[B];
            DISPATCH(1);

        MOVBC:
            regs[B] = regs[C];
            DISPATCH(1);

        MOVBD:
            regs[B] = regs[D];
            DISPATCH(1);

        MOVBE:
            regs[B] = regs[E];
            DISPATCH(1);

        MOVBH:
            regs[B] = regs[H];
            DISPATCH(1);

        MOVBL:
            regs[B] = regs[L];
            DISPATCH(1);

        MOVBMHL:
            regs[B] = mem[regs.HL()];
            DISPATCH(1);

        MOVBA:
            regs[B] = regs[A];
            DISPATCH(1);

        MOVCB:
            regs[C] = regs[B];
            DISPATCH(1);

        MOVCC:
            regs[C] = regs[C];
            DISPATCH(1);

        MOVCD:
            regs[C] = regs[D];
            DISPATCH(1);

        MOVCE:
            regs[C] = regs[E];
            DISPATCH(1);

        MOVCH:
            regs[C] = regs[H];
            DISPATCH(1);

        MOVCL:
            regs[C] = regs[L];
            DISPATCH(1);

        MOVCMHL:
            regs[C] = mem[regs.HL()];
            DISPATCH(1);

        MOVCA:
            regs[C] = regs[A];
            DISPATCH(1);

        MOVDB:
            regs[D] = regs[B];
            DISPATCH(1);

        MOVDC:
            regs[D] = regs[C];
            DISPATCH(1);

        MOVDD:
            regs[D] = regs[D];
            DISPATCH(1);

        MOVDE:
            regs[D] = regs[E];
            DISPATCH(1);

        MOVDH:
            regs[D] = regs[H];
            DISPATCH(1);

        MOVDL:
            regs[D] = regs[L];
            DISPATCH(1);

        MOVDMHL:
            regs[D] = mem[regs.HL()];
            DISPATCH(1);

        MOVDA:
            regs[D] = regs[A];
            DISPATCH(1);

        MOVEB:
            regs[E] = regs[B];
            DISPATCH(1);

        MOVEC:
            regs[E] = regs[C];
            DISPATCH(1);

        MOVED:
            regs[E] = regs[D];
            DISPATCH(1);

        MOVEE:
            regs[E] = regs[E];
            DISPATCH(1);

        MOVEH:
            regs[E] = regs[H];
            DISPATCH(1);

        MOVEL:
            regs[E] = regs[L];
            DISPATCH(1);

        MOVEMHL:
            regs[E] = mem[regs.HL()];
            DISPATCH(1);

        MOVEA:
            regs[E] = regs[A];
            DISPATCH(1);

        MOVHB:
            regs[H] = regs[B];
            DISPATCH(1);

        MOVHC:
            regs[H] = regs[C];
            DISPATCH(1);

        MOVHD:
            regs[H] = regs[D];
            DISPATCH(1);

        MOVHE:
            regs[H] = regs[E];
            DISPATCH(1);

        MOVHH:
            regs[H] = regs[H];
            DISPATCH(1);

        MOVHL:
            regs[H] = regs[L];
            DISPATCH(1);

        MOVHMHL:
            regs[H] = mem[regs.HL()];
            DISPATCH(1);

        MOVHA:
            regs[H] = regs[A];
            DISPATCH(1);

        MOVLB:
            regs[L] = regs[B];
            DISPATCH(1);

        MOVLC:
            regs[L] = regs[C];
            DISPATCH(1);

        MOVLD:
            regs[L] = regs[D];
            DISPATCH(1);

        MOVLE:
            regs[L] = regs[E];
            DISPATCH(1);

        MOVLH:
            regs[L] = regs[H];
            DISPATCH(1);

        MOVLL:
            regs[L] = regs[L];
            DISPATCH(1);

        MOVLMHL:
            regs[L] = mem[regs.HL()];
            DISPATCH(1);

        MOVLA:
            regs[L] = regs[A];
            DISPATCH(1);

        MOVMHLB:
            mem[regs.HL()] = regs[B];
            DISPATCH(1);

        MOVMHLC:
            mem[regs.HL()] = regs[C];
            DISPATCH(1);

        MOVMHLD:
            mem[regs.HL()] = regs[D];
            DISPATCH(1);

        MOVMHLE:
            mem[regs.HL()] = regs[E];
            DISPATCH(1);

        MOVMHLH:
            mem[regs.HL()] = regs[H];
            DISPATCH(1);

        MOVMHLL:
            mem[regs.HL()] = regs[L];
            DISPATCH(1);

        MOVMHLA:
            mem[regs.HL()] = regs[A];
            DISPATCH(1);

        MOVAB:
            regs[A] = regs[B];
            DISPATCH(1);

        MOVAC:
            regs[A] = regs[C];
            DISPATCH(1);

        MOVAD:
            regs[A] = regs[D];
            DISPATCH(1);

        MOVAE:
            regs[A] = regs[E];
            DISPATCH(1);

        MOVAH:
            regs[A] = regs[H];
            DISPATCH(1);

        MOVAL:
            regs[A] = regs[L];
            DISPATCH(1);

        MOVAMHL:
            regs[A] = mem[regs.HL()];
            DISPATCH(1);

        MOVAA:
            regs[A] = regs[A];
            DISPATCH(1);

        MOVHLBC:
            regs[H] = regs[B];
            regs[L] = regs[C];
            DISPATCH(1);

        MOVHLDE:
            regs[H] = regs[D];
            regs[L] = regs[E];
            DISPATCH(1);

        // ----------------------------------------
        // 2.2 Arithmetic
        // ----------------------------------------

        // 2.2.1 Flag Setting

        CLRFLAG:
            regs.set_ZFLAG(false);
            regs.set_NFLAG(false);
            regs.set_HFLAG(false);
            regs.set_CFLAG(false);
            DISPATCH(1);

        SETFLAGZ1:
            regs.set_ZFLAG(true);
            DISPATCH(1);

        SETFLAGZ0:
            regs.set_ZFLAG(false);
            DISPATCH(1);

        SETFLAGN1:
            regs.set_NFLAG(true);
            DISPATCH(1);

        SETFLAGN0:
            regs.set_NFLAG(false);
            DISPATCH(1);

        SETFLAGH1:
            regs.set_HFLAG(true);
            DISPATCH(1);

        SETFLAGH0:
            regs.set_HFLAG(false);
            DISPATCH(1);

        SETFLAGC1:
            regs.set_CFLAG(true);
            DISPATCH(1);

        SETFLAGC0:
            regs.set_CFLAG(false);
            DISPATCH(1);

        // 2.2.2 Addition

        ADDB:
            ADD_8(regs[B], regs[A], 1);

        ADDC:
            ADD_8(regs[C], regs[A], 1);

        ADDD:
            ADD_8(regs[D], regs[A], 1);

        ADDE:
            ADD_8(regs[E], regs[A], 1);

        ADDH:
            ADD_8(regs[H], regs[A], 1);

        ADDL:
            ADD_8(regs[L], regs[A], 1);

        ADDMHL:
            ADD_8(mem[regs.HL()], regs[A], 1);

        ADDA:
            ADD_8(regs[A], regs[A], 1);

        ADDI:
            ADD_8(regs[A], mem[pc+1], 2);

        ADDBC:
            ADD_16(regs[B], regs[C], regs[A], 1);

        ADDDE:
            ADD_16(regs[D], regs[E], regs[A], 1);

        ADDHL:
            ADD_16(regs[H], regs[L], regs[A], 1);

        // 2.2.3 Subtraction

        SUBB:
            SUB_8(regs[B], regs[A], 1);

        SUBC:
            SUB_8(regs[C], regs[A], 1);

        SUBD:
            SUB_8(regs[D], regs[A], 1);

        SUBE:
            SUB_8(regs[E], regs[A], 1);

        SUBH:
            SUB_8(regs[H], regs[A], 1);

        SUBL:
            SUB_8(regs[L], regs[A], 1);

        SUBMHL:
            SUB_8(mem[regs.HL()], regs[A], 1);

        SUBA:
            SUB_8(regs[A], regs[A], 1);

        SUBI:
            SUB_8(regs[A], mem[pc+1], 2);

        // 2.2.4 Increment

        INCB:
            ADD_8(regs[B], 1, 1);

        INCC:
            ADD_8(regs[C], 1, 1);

        INCD:
            ADD_8(regs[D], 1, 1);

        INCE:
            ADD_8(regs[E], 1, 1);

        INCH:
            ADD_8(regs[H], 1, 1);

        INCL:
            ADD_8(regs[L], 1, 1);

        INCMHL:
            ADD_8(mem[regs.HL()], 1, 1);

        INCA:
            ADD_8(regs[A], 1, 1);

        // These 3 INCs don't set flags!
        INCBC:
            regs.set_BC(regs.BC()+1);
            DISPATCH(1);

        INCDE:
            regs.set_DE(regs.DE()+1);
            DISPATCH(1);

        INCHL:
            regs.set_HL(regs.HL()+1);
            DISPATCH(1);

        // 2.2.5 Decrement

        DECB:
            SUB_8(regs[B], 1, 1);

        DECC:
            SUB_8(regs[C], 1, 1);

        DECD:
            SUB_8(regs[D], 1, 1);

        DECE:
            SUB_8(regs[E], 1, 1);

        DECH:
            SUB_8(regs[H], 1, 1);

        DECL:
            SUB_8(regs[L], 1, 1);

        DECMHL:
            SUB_8(mem[regs.HL()], 1, 1);

        DECA:
            SUB_8(regs[A], 1, 1);

        // ----------------------------------------
        // 2.3 Logical Operations
        // ----------------------------------------

        // 2.3.1 AND

        ANDB:
            NZ_FLAGS_OP_8(&, regs[B], regs[A], 1);

        ANDC:
            NZ_FLAGS_OP_8(&, regs[C], regs[A], 1);

        ANDD:
            NZ_FLAGS_OP_8(&, regs[D], regs[A], 1);

        ANDE:
            NZ_FLAGS_OP_8(&, regs[E], regs[A], 1);

        ANDH:
            NZ_FLAGS_OP_8(&, regs[H], regs[A], 1);

        ANDL:
            NZ_FLAGS_OP_8(&, regs[L], regs[A], 1);

        ANDMHL:
            NZ_FLAGS_OP_8(&, mem[regs.HL()], regs[A], 1);

        ANDA:
            NZ_FLAGS_OP_8(&, regs[A], regs[A], 1);

        ANDI:
            NZ_FLAGS_OP_8(&, regs[A], mem[pc+1], 2);

        // 2.3.2 OR

        ORB:
            NZ_FLAGS_OP_8(|, regs[B], regs[A], 1);

        ORC:
            NZ_FLAGS_OP_8(|, regs[C], regs[A], 1);

        ORD:
            NZ_FLAGS_OP_8(|, regs[D], regs[A], 1);

        ORE:
            NZ_FLAGS_OP_8(|, regs[E], regs[A], 1);

        ORH:
            NZ_FLAGS_OP_8(|, regs[H], regs[A], 1);

        ORL:
            NZ_FLAGS_OP_8(|, regs[L], regs[A], 1);

        ORMHL:
            NZ_FLAGS_OP_8(|, mem[regs.HL()], regs[A], 1);

        ORA:
            NZ_FLAGS_OP_8(|, regs[A], regs[A], 1);

        ORI:
            NZ_FLAGS_OP_8(|, regs[A], mem[pc+1], 2);

        // 2.3.3 XOR

        XORB:
            NZ_FLAGS_OP_8(^, regs[B], regs[A], 1);

        XORC:
            NZ_FLAGS_OP_8(^, regs[C], regs[A], 1);

        XORD:
            NZ_FLAGS_OP_8(^, regs[D], regs[A], 1);

        XORE:
            NZ_FLAGS_OP_8(^, regs[E], regs[A], 1);

        XORH:
            NZ_FLAGS_OP_8(^, regs[H], regs[A], 1);

        XORL:
            NZ_FLAGS_OP_8(^, regs[L], regs[A], 1);

        XORMHL:
            NZ_FLAGS_OP_8(^, mem[regs.HL()], regs[A], 1);

        XORA:
            NZ_FLAGS_OP_8(^, regs[A], regs[A], 1);

        XORI:
            NZ_FLAGS_OP_8(^, regs[A], mem[pc+1], 2);

        // 2.3.4 Comparisons

        CMPB:
            res8 = regs[B];
            SUB_8(res8, regs[A], 1);

        CMPC:
            res8 = regs[C];
            SUB_8(res8, regs[A], 1);

        CMPD:
            res8 = regs[D];
            SUB_8(res8, regs[A], 1);

        CMPE:
            res8 = regs[E];
            SUB_8(res8, regs[A], 1);

        CMPH:
            res8 = regs[H];
            SUB_8(res8, regs[A], 1);

        CMPL:
            res8 = regs[L];
            SUB_8(res8, regs[A], 1);

        CMPMHL:
            res8 = mem[regs.HL()];
            SUB_8(res8, regs[A], 1);

        CMPA:
            res8 = regs[A];
            SUB_8(res8, regs[A], 1);

        CMPI:
            res8 = regs[A];
            SUB_8(res8, mem[pc+1], 2);

        CMPSB:
            res8 = regs[B];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSC:
            res8 = regs[C];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSD:
            res8 = regs[D];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSE:
            res8 = regs[E];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSH:
            res8 = regs[H];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSL:
            res8 = regs[L];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSMHL:
            res8 = mem[regs.HL()];
            SIGNED_SUB_8(res8, regs[A], 1);

        CMPSA:
            res8 = regs[A];
            SIGNED_SUB_8(res8, regs[A], 1);

        // ----------------------------------------
        // 2.4 I/O
        // ----------------------------------------

        // 2.4.1 Serial

        SIN:
            regs[A] = fgetc(stdin);
            DISPATCH(1);

        SOUT:
            std::cout << regs[A];
            DISPATCH(1);

        // 2.4.2 Screen

        CLRSCR:
            clearscreen();
            DISPATCH(1);

        DRAW:
            draw();
            DISPATCH(1);

        // ----------------------------------------
        // 2.5 Branching
        // ----------------------------------------

        // 2.5.1 Jumping

        JMP:
            pc = mem.get_word(pc+1);
            DISPATCH(0);

        JMPZ:
            pc = regs.ZFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPNZ:
            pc = !regs.ZFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPN:
            pc = regs.NFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPNN:
            pc = !regs.NFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPH:
            pc = regs.HFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPNH:
            pc = !regs.HFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPC:
            pc = regs.CFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        JMPNC:
            pc = !regs.CFLAG() ? mem.get_word(pc+1) : pc+3;
            DISPATCH(0);

        // 2.5.2 Near-Jumping

        JMPXX:
            pc = pc+2 + (int8_t) mem[pc+1];
            DISPATCH(0);

        JMPXXZ:
            pc = regs.ZFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXNZ:
            pc = !regs.ZFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXN:
            pc = regs.NFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXNN:
            pc = !regs.NFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXH:
            pc = regs.HFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXNH:
            pc = !regs.HFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXC:
            pc = regs.CFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        JMPXXNC:
            pc = !regs.CFLAG() ? (pc+2 + (int8_t) mem[pc+1]) : pc+2;
            DISPATCH(0);

        // 2.5.3 Functions

        CALL:
            mem.set_word(sp, pc+3);
            sp -= 2;
            pc = mem.get_word(pc+1);
            DISPATCH(0);

        RET:
            sp += 2;
            pc = mem.get_word(sp);
            DISPATCH(0);

        // ----------------------------------------
        // 2.6 Miscellaneous
        // ----------------------------------------

        // 2.6.1 No Operation

        NOP:
            DISPATCH(1);

        // 2.6.2 Halt and Catch Fire

        HCF:
            break;

        UNKNOWN_OP:
            std::cout << "Unknown opcode '" << unsigned(mem[pc]) << "' at PC '" << unsigned(pc) << "'; exiting." << std::endl;
            return;
    }
    std::cout << "\nProgram halted." << std::endl;
}

void Emulator::clearscreen()
{
    // keeping the update here means the image stays on the screen longer
    this->screen->update(pixels);
    this->screen->render();

    // now, clear the screen and start drawing next frame
    // the current frame won't get deleted until the previous frame is finished
    for (size_t row = 0; row < 64; row++)
    {
        for (size_t col = 0; col < 128; col++)
        {
            pixels[row][col] = 0;
        }
    }
}

void Emulator::draw()
{
    // CHIP-9 draws one byte at a time to the frame
    // Re-rendering for each update causes slow rendering
    // One solution is to only render the buffer when the "whole" picture is painted
    // This is usually true right before a call to clear the screen.

    // So, in this method, we do not attempt to render or update the screen.

    int8_t x = regs[C];
    int8_t y = regs[B];
    for (size_t i = 0; i < 8; i++)
    {
        if (x + i >= 0 && x + i < 128)
        {
            uint8_t bit = regs[A] & (1 << (7-i));
            pixels[y][x+i] = bit;
        }
    }
}

std::string Emulator::inst_repr()
{
    std::stringstream sstream;
    std::string inst = names[mem[pc]];

    if (inst.rfind("LDI", 0) == 0
        || inst.rfind("ADDI", 0) == 0
        || inst.rfind("SUBI", 0) == 0
        || inst.rfind("ANDI", 0) == 0
        || inst.rfind("ORI", 0) == 0
        || inst.rfind("XORI", 0) == 0
        || inst.rfind("CMPI", 0) == 0
        || inst.rfind("RELJMP", 0) == 0)
    {
        sstream << std::hex << unsigned(mem[pc+1]);
        inst += ", 0x" + sstream.str();
    }
    else if (inst.rfind("LDX", 0) == 0
        || inst.rfind("JMP", 0) == 0
        || inst.rfind("CALL", 0) == 0)
    {
        sstream << std::hex << unsigned(mem.get_word(pc+1));
        inst += ", 0x" + sstream.str();
    }
    return inst;
}
