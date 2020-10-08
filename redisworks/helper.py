import sys

py_major_version = sys.version[0]
py_minor_version = sys.version[2]

if int(py_major_version) < 3:  # pragma: no cover
    sys.exit('Python 2 is not supported anymore.')
