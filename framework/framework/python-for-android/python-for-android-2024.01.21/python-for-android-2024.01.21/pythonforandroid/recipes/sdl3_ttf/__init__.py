from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL3TTF(BootstrapNDKRecipe):
    version = '3.0.0'
    url = 'https://github.com/libsdl-org/SDL_ttf/releases/download/release-{version}/SDL3_ttf-{version}.tar.gz'
    dir_name = 'SDL3_ttf'

    depends = ['harfbuzz', 'freetype']


recipe = LibSDL3TTF()
