version = "0.4"
from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    mcpath = "/.minecraft"
elif _platform == "darwin":
    mcpath = "/Library/Application Support/minecraft"
elif _platform in ("win32","cygwin"):
    mcpath = "/AppData/Roaming/.minecraft"