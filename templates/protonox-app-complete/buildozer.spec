[app]
title = Protonox App Complete
package.name = protonox_app_complete
package.domain = org.protonox
source.dir = app
source.exclude_dirs = tests,venv,.venv
orientation = portrait
fullscreen = 0
log_level = 2
requirements = python3,kivy==2.3.1,requests
android.api = 35
android.minapi = 24
android.ndk = 26b
android.allow_backup = True
p4a.local_recipes = ../framework/python-for-android/recipes

[buildozer]
log_level = 2
warn_on_root = 1
