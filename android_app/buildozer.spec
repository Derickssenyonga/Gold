[app]
# (str) Title of your application
title = GoldScalper

# (str) Package name
package.name = goldscalper

# (str) Package domain (needed for android/aidl)
domain = org.example

# (str) Package version
version = 1.0

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
requirements = python3,kivy

# (str) Presplash of the app
presplash.filename = %(source.dir)s/data/presplash.png

# (str) Orientation of the app
orientation = portrait

# (bool) Indicate if the app should be multi-process
# android.no-compile-python = True

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (int) Target Android API, should be as high as possible.
android.api = 34

# (str) Android package architecture
android.archs = arm64-v8a

# (list) Android permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (list) List of Java files to add to the project
# android.add_jars = foo.jar

[build]
# (int) Verbosity level
verbosity = 2

[python]
# (int) python version
# python.version = 3

[buildozer]
# (int) Log level
log_level = 2
