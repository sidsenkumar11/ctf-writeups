#pragma once
#include <SDL2/SDL.h>
#include <string>

// Display each pixel as a square so it's easier to see
#define PIXEL_SIZE 5

// Prevent rendering so fast that message becomes hard to see
#define FPS_CAP 60
#define MIN_MS_PER_FRAME (1000.0 / FPS_CAP)

template<size_t rows, size_t cols>
class Screen {
    private:
        SDL_Window *window;
        SDL_Renderer *renderer;
        SDL_Rect **rects;
        int32_t prev_render_timestamp;
    public:
        Screen(std::string title);
        virtual void handleEvents();
        virtual void update(uint8_t (&pixels)[rows][cols]);
        virtual void render();
};

#include "Screen.tpp"
