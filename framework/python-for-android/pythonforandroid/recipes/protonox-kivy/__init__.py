from os.path import join, exists
import os
import sys
import packaging.version

import sh
from pythonforandroid.recipe import Recipe
from pythonforandroid.toolchain import current_directory, shprint
from pythonforandroid.util import ensure_dir


def is_protonox_kivy_affected_by_deadlock_issue(recipe=None, arch=None):
    # Since we're using protonox-kivy 3.0.0.dev10, which is newer than 2.2.0.dev0,
    # we're not affected by the deadlock issue that required the sdl-gl-swapwindow-nogil.patch
    return False


class ProtonoxKivyRecipe(Recipe):
    version = '3.0.0.dev10'
    # Use local source instead of downloading
    url = None
    name = 'protonox-kivy'

    @property
    def source_dir(self):
        # Use the local kivy-protonox-version directory
        return '/home/protonox/Protonox-Kivy-Multiplatform-Framework/kivy-protonox-version'

    def prepare_build_dir(self, arch):
        # Copy local source to build directory
        build_dir = self.get_build_dir(arch)
        if exists(build_dir):
            return
        ensure_dir(self.get_build_container_dir(arch))
        shprint(sh.cp, '-a', self.source_dir, build_dir)

    depends = [('sdl2', 'sdl3'), 'pyjnius', 'setuptools', 'android']
    python_depends = ['certifi', 'chardet', 'idna', 'requests', 'urllib3', 'filetype']
    hostpython_prerequisites = ["cython>=0.29.1,<=3.0.12"]

    # sdl-gl-swapwindow-nogil.patch is needed to avoid a deadlock.
    # See: https://github.com/kivy/kivy/pull/8025
    # WARNING: Remove this patch when a new Kivy version is released.
    patches = [
        ("sdl-gl-swapwindow-nogil.patch", is_protonox_kivy_affected_by_deadlock_issue),
        "use_cython.patch",
        "no-ast-str.patch"
    ]

    def build_arch(self, arch):
        # Build and install kivy using setup.py
        env = self.get_recipe_env(arch)
        hostpython = sh.Command(self.ctx.hostpython)

        self.ctx.logger.info(f'🔨 Building Protonox-Kivy for {arch.arch} with cross-compilation...')

        try:
            with current_directory(self.get_build_dir(arch.arch)):
                self.ctx.logger.info('📦 Installing Protonox-Kivy with ARM64 cross-compilation...')
                shprint(hostpython, 'setup.py', 'install',
                       '--prefix={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                       '--plat-name=linux-aarch64', _env=env)
                self.ctx.logger.info('✅ Protonox-Kivy build completed successfully')
        except sh.ErrorReturnCode as e:
            self.ctx.logger.error(f'❌ Protonox-Kivy build failed: {e}')
            self.ctx.logger.error('🔍 Common issues:')
            self.ctx.logger.error('   - Check NDK version (should be r28+)')
            self.ctx.logger.error('   - Verify cross-compilation environment variables')
            self.ctx.logger.error('   - Ensure Cython is available in hostpython')
            self.ctx.logger.error('   - See docs/ANDROID_BUILD_LESSONS.md for details')
            raise

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)

        # Ensure cross-compilation for Android
        hostpython_lib_site_packages = os.path.join(os.path.dirname(self.ctx.hostpython), 'root', 'usr', 'local', 'lib', 'python3.14', 'site-packages')
        user_site_packages = '/home/protonox/.local/lib/python3.14/site-packages'
        env['PYTHONPATH'] = user_site_packages + ':' + hostpython_lib_site_packages + ':' + join(self.ctx.get_python_install_dir(arch.arch), 'site-packages')
        
        # Set cross-compilation environment variables
        clang = join(self.ctx.ndk_dir, 'toolchains', 'llvm', 'prebuilt', 'linux-x86_64', 'bin', 'clang')
        clangxx = join(self.ctx.ndk_dir, 'toolchains', 'llvm', 'prebuilt', 'linux-x86_64', 'bin', 'clang++')
        
        env['CC'] = '{} -target {}-linux-android{}'.format(clang, arch.arch.replace('arm64', 'aarch64'), self.ctx.ndk_api)
        env['CXX'] = '{} -target {}-linux-android{}'.format(clangxx, arch.arch.replace('arm64', 'aarch64'), self.ctx.ndk_api)
        env['CFLAGS'] = '-fomit-frame-pointer -march=armv8-a -fPIC -I{} -I{} -I{} -DANDROID -D__ANDROID_API__={}'.format(
            join(self.ctx.get_python_install_dir(arch.arch), 'include', 'python3.12'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
            join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include'),
            self.ctx.ndk_api
        )
        env['LDFLAGS'] = '-L{} -L{}'.format(
            join(self.ctx.libs_dir, arch.arch),
            join(self.ctx.ndk_dir, 'toolchains', 'llvm', 'prebuilt', 'linux-x86_64', 'sysroot', 'usr', 'lib', 'aarch64-linux-android', str(self.ctx.ndk_api))
        )
        env['CPPFLAGS'] = '-D__ANDROID_API__={}'.format(self.ctx.ndk_api)
        
        # Completely isolate from host system
        env['C_INCLUDE_PATH'] = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')
        env['CPLUS_INCLUDE_PATH'] = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')
        env['LIBRARY_PATH'] = join(self.ctx.ndk_dir, 'toolchains', 'llvm', 'prebuilt', 'linux-x86_64', 'sysroot', 'usr', 'lib', 'aarch64-linux-android', str(self.ctx.ndk_api))
        
        # Remove any host system include paths that might cause conflicts
        env['CPATH'] = join(self.ctx.ndk_dir, 'sysroot', 'usr', 'include')
        
        # Force cross-compilation platform detection
        env['_PYTHON_HOST_PLATFORM'] = 'linux-aarch64'
        
        env['LDFLAGS'] += ' -L{} -L{} -L{} -L{}'.format(
            self.ctx.get_libs_dir(arch.arch),
            self.ctx.libs_dir,
            join(self.ctx.bootstrap.build_dir, 'obj', 'local', arch.arch),
            join(self.ctx.get_python_install_dir(arch.arch), 'lib')
        )

        # Taken from CythonRecipe
        env['LDFLAGS'] = env['LDFLAGS'] + ' -L{} '.format(
            self.ctx.get_libs_dir(arch.arch) +
            ' -L{} '.format(self.ctx.libs_dir) +
            ' -L{}'.format(join(self.ctx.bootstrap.build_dir, 'obj', 'local',
                                arch.arch)))
        env['LDSHARED'] = env['CC'] + ' -shared'
        env['LIBLINK'] = 'NOTNONE'

        # NDKPLATFORM is our switch for detecting Android platform, so can't be None
        env['NDKPLATFORM'] = "NOTNONE"
        if 'sdl2' in self.ctx.recipe_build_order:
            env['USE_SDL2'] = '1'
            env['KIVY_SPLIT_EXAMPLES'] = '1'
            sdl2_mixer_recipe = self.get_recipe('sdl2_mixer', self.ctx)
            sdl2_image_recipe = self.get_recipe('sdl2_image', self.ctx)
            env['KIVY_SDL2_PATH'] = ':'.join([
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
                *sdl2_image_recipe.get_include_dirs(arch),
                *sdl2_mixer_recipe.get_include_dirs(arch),
                join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
            ])
        if "sdl3" in self.ctx.recipe_build_order:
            sdl3_mixer_recipe = self.get_recipe("sdl3_mixer", self.ctx)
            sdl3_image_recipe = self.get_recipe("sdl3_image", self.ctx)
            sdl3_ttf_recipe = self.get_recipe("sdl3_ttf", self.ctx)
            sdl3_recipe = self.get_recipe("sdl3", self.ctx)
            env["USE_SDL3"] = "1"
            env["KIVY_SPLIT_EXAMPLES"] = "1"
            env["KIVY_SDL3_PATH"] = ":".join(
                [
                    *sdl3_mixer_recipe.get_include_dirs(arch),
                    *sdl3_image_recipe.get_include_dirs(arch),
                    *sdl3_ttf_recipe.get_include_dirs(arch),
                    *sdl3_recipe.get_include_dirs(arch),
                ]
            )

        # Add Android-specific compile options to fix glibc macro issues
        env['CFLAGS'] += ' -D__GNUC_PREREQ(maj,min)=1 -D__glibc_clang_prereq(maj,min)=0'

        return env


recipe = ProtonoxKivyRecipe()