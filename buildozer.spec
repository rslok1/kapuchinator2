[app]
title = Капучинатор
package.name = capuchinator
package.domain = org.fixiki
source.dir = .
source.include_exts = py,png,jpg,jpeg,mp3,wav
version = 0.1
requirements = python3,pygame
orientation = landscape
fullscreen = 1

[buildozer]
log_level = 2
warn_on_root = 1

[android]
fullscreen = 1
android.archs = arm64-v8a
android.api = 33
android.min_api = 21
android.accept_sdk_license = True
