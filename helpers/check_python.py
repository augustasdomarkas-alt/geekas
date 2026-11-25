"""Run first: python helpers/check_python.py (works without Flask)."""
import platform
import sqlite3
import sys

print("Python version:", sys.version.split()[0])
print("Operating system:", platform.system())
print("SQLite version:", sqlite3.sqlite_version)
try:
    import flask
    print("Flask installed: YES")
except ModuleNotFoundError:
    print("Flask installed: NO - follow 02_INSTALL_AND_SETUP.txt")
print("Next: run python app.py from the server folder")
