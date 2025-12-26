import os

from pythonforandroid.recipe import BootstrapNDKRecipe


class LibSDL3Mixer(BootstrapNDKRecipe):
    version = '3.0.0'
    url = 'https://github.com/libsdl-org/SDL_mixer/releases/download/release-{version}/SDL3_mixer-{version}.tar.gz'
    dir_name = 'SDL3_mixer'

    def get_include_dirs(self, arch):
        return [
            os.path.join(self.ctx.bootstrap.build_dir, "jni", "SDL3_mixer", "include")
        ]


recipe = LibSDL3Mixer()
