from pythonforandroid.recipe import PythonRecipe


class MesonRecipe(PythonRecipe):
    """
    Recipe for meson build system. Meson is required for building
    modern numpy versions that use meson-python.
    """
    version = '1.4.0'
    url = 'https://pypi.python.org/packages/source/m/meson/meson-{version}.tar.gz'
    depends = []
    site_packages_name = 'meson'
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        return env


recipe = MesonRecipe()