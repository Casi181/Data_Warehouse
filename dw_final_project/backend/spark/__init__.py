import os
import sys
from pathlib import Path

# On Windows, Spark requires HADOOP_HOME with winutils.exe
if sys.platform == "win32" and "HADOOP_HOME" not in os.environ:
    _hadoop_dir = str(Path(__file__).resolve().parent.parent / "hadoop")
    os.environ["HADOOP_HOME"] = _hadoop_dir
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + str(Path(_hadoop_dir) / "bin")
