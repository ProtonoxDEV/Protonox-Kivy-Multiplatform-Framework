from pythonforandroid.recipe import PythonRecipe


class MesonPythonRecipe(PythonRecipe):
    """
    Recipe for meson-python, the Python build backend for Meson.
    Required for building numpy with modern meson-based builds.
    """
    version = '0.15.1'
    url = 'https://pypi.python.org/packages/source/m/meson-python/meson-python-{version}.tar.gz'
    depends = ['meson']
    site_packages_name = 'meson_python'
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch, with_flags_in_cc)
        return env


recipe = MesonPythonRecipe()