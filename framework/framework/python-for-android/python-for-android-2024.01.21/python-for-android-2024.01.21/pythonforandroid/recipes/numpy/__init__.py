from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
from multiprocessing import cpu_count
from os.path import join
import glob
import sh
import shutil


class NumpyRecipe(CompiledComponentsPythonRecipe):

    version = '1.26.4'
    url = 'https://pypi.python.org/packages/source/n/numpy/numpy-{version}.tar.gz'
    site_packages_name = 'numpy'
    depends = ['setuptools', 'cython', 'meson', 'meson-python']
    install_in_hostpython = True
    call_hostpython_via_targetpython = False

    patches = [
        join("patches", "remove-default-paths.patch"),
        join("patches", "add_libm_explicitly_to_build.patch"),
        join("patches", "ranlib.patch"),
    ]

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)

        # _PYTHON_HOST_PLATFORM declares that we're cross-compiling
        # and avoids issues when building on macOS for Android targets.
        env["_PYTHON_HOST_PLATFORM"] = arch.command_prefix

        # NPY_DISABLE_SVML=1 allows numpy to build for non-AVX512 CPUs
        # See: https://github.com/numpy/numpy/issues/21196
        env["NPY_DISABLE_SVML"] = "1"

        # Ensure meson is available in PATH for meson-python
        import os
        hostpython_dir = os.path.dirname(self.hostpython_location)
        env["PATH"] = f"{hostpython_dir}:{env.get('PATH', '')}"

        return env

    def _build_compiled_components(self, arch):
        info('Building compiled components in {}'.format(self.name))

        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            # Create meson cross-file for Android
            self._create_meson_cross_file(arch, env)

            hostpython = sh.Command(self.hostpython_location)
            # Use modern build system with meson
            build_args = [
                '-m', 'build', '--wheel',
                '--config-setting', 'builddir=p4a_android_build',
                '-Csetup-args=-Dblas=none',
                '-Csetup-args=-Dlapack=none',
                '-Csetup-args=--cross-file',
                '-Csetup-args=/tmp/android.meson.cross'
            ]
            if self.setup_extra_args:
                build_args.extend(self.setup_extra_args)
            shprint(hostpython, *build_args, _env=env)
            build_dir = glob.glob('build/lib.*')[0]
            shprint(sh.find, build_dir, '-name', '"*.o"', '-exec',
                    env['STRIP'], '{}', ';', _env=env)

    def _rebuild_compiled_components(self, arch, env):
        info('Rebuilding compiled components in {}'.format(self.name))

        # Create meson cross-file for Android
        self._create_meson_cross_file(arch, env)

        hostpython = sh.Command(self.real_hostpython_location)
        # Clean build directory
        shprint(hostpython, '-m', 'build', '--wheel', '--clean', _env=env)
        # Rebuild with modern build system
        build_args = [
            '-m', 'build', '--wheel',
            '--config-setting', 'builddir=p4a_android_build',
            '-Csetup-args=-Dblas=none',
            '-Csetup-args=-Dlapack=none',
            '-Csetup-args=--cross-file',
            '-Csetup-args=/tmp/android.meson.cross'
        ]
        if self.setup_extra_args:
            build_args.extend(self.setup_extra_args)
        shprint(hostpython, *build_args, _env=env)

    def build_compiled_components(self, arch):
        self.setup_extra_args = ['-j', str(cpu_count())]
        self._build_compiled_components(arch)
        self.setup_extra_args = []

    def rebuild_compiled_components(self, arch, env):
        self.setup_extra_args = ['-j', str(cpu_count())]
        self._rebuild_compiled_components(arch, env)
        self.setup_extra_args = []

    def get_hostrecipe_env(self, arch):
        env = super().get_hostrecipe_env(arch)
        env['RANLIB'] = shutil.which('ranlib')
        return env

    def _create_meson_cross_file(self, arch, env):
        """Create meson cross-compilation file for Android"""
        cross_file_content = f'''[binaries]
c = '{env.get("CC", "gcc")}'
cpp = '{env.get("CXX", "g++")}'
ar = '{env.get("AR", "ar")}'
strip = '{env.get("STRIP", "strip")}'
pkgconfig = 'pkg-config'

[host_machine]
system = 'android'
cpu_family = '{arch.command_prefix.split("-")[0]}'
cpu = '{arch.command_prefix}'
endian = 'little'

[properties]
sys_root = '{env.get("SYSROOT", "")}'
'''
        with open('/tmp/android.meson.cross', 'w') as f:
            f.write(cross_file_content)


recipe = NumpyRecipe()
