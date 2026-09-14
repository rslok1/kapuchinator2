[app]
title = Capuchinator
package.name = capuchinator
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
orientation = portrait
requirements = python3==3.11,pygame
p4a.args = --python-version=3.11 --hostpython-version=3.11
p4a.source_dir = https://github.com/kivy/python-for-android
p4a.branch = master
android.ndk_api = 24
android.api = 36
