.DEFAULT_GOAL := bin/emulator

CXX=g++
CFLAGS=-std=c++17 -g -Wall
LFLAGS=-lstdc++fs -lSDL2main -lSDL2 -lSDL2_image
CPPS=$(shell find src -type f -name '*.cpp')
OBJS=$(patsubst src/%.cpp, build/%.o, $(CPPS))
DEPS=$(OBJS:%.o=%.d)

bin:
	mkdir -p bin

bin/emulator: | bin
bin/emulator: $(OBJS) build/main.o
	$(CXX) $(CFLAGS) -o $@ $^ $(LFLAGS)

-include $(DEPS)

build:
	mkdir build

$(OBJS): | build

build/%.o: src/%.cpp
	$(CXX) $(CFLAGS) -MMD -c -o $@ $< $(LFLAGS)

.PHONY: clean
clean:
	$(RM) -r bin build
