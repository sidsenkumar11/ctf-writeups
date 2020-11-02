template<size_t rows, size_t cols>
Screen<rows, cols>::Screen(std::string title)
{
    // create window and renderer
    SDL_Init(SDL_INIT_EVERYTHING);
    SDL_DisplayMode DM;
    SDL_GetCurrentDisplayMode(0, &DM);
    size_t startX = (DM.w-cols)/2 - 200;
    size_t startY = (DM.h-rows)/2 - 100;
    window = SDL_CreateWindow(title.c_str(), startX, startY, cols*PIXEL_SIZE, rows*PIXEL_SIZE, 0);
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    prev_render_timestamp = SDL_GetTicks();

    // cache rectangles for faster renders
    this->rects = new SDL_Rect *[rows];
    for (size_t i = 0; i < rows; i++)
    {
        this->rects[i] = new SDL_Rect[cols];
    }
    for(size_t i = 0; i < rows; i++)
    {
        for(size_t j = 0; j < cols; j++)
        {
            SDL_Rect *rect = &rects[i][j];
            rect->x = j*PIXEL_SIZE;
            rect->y = i*PIXEL_SIZE;
            rect->w = PIXEL_SIZE;
            rect->h = PIXEL_SIZE;
        }
    }

    // clear screen
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
    SDL_RenderClear(renderer);
}

template<size_t rows, size_t cols>
void Screen<rows, cols>::handleEvents()
{
    SDL_Event event;
    SDL_PollEvent(&event);

    switch(event.type)
    {
        case SDL_QUIT:
            SDL_Quit();
            exit(1);
        default:
            break;
    }
}

template<size_t rows, size_t cols>
void Screen<rows, cols>::update(uint8_t (&pixels)[rows][cols])
{
    for(size_t i = 0; i < rows; i++)
    {
        for (size_t j = 0; j < cols; j++)
        {
            if (pixels[i][j])
            {
                SDL_SetRenderDrawColor(renderer, 0, 100, 0, 255);
            }
            else
            {
                SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
            }
            SDL_RenderFillRect(renderer, &rects[i][j]);
        }
    }
}

template<size_t rows, size_t cols>
void Screen<rows, cols>::render()
{
    // FPS Cap to prevent tearing
    uint32_t ms_since_last_render = SDL_GetTicks() - prev_render_timestamp;
    if (ms_since_last_render < MIN_MS_PER_FRAME)
    {
        SDL_Delay(MIN_MS_PER_FRAME - ms_since_last_render);
    }

    SDL_RenderPresent(renderer);
    prev_render_timestamp = SDL_GetTicks();
}
