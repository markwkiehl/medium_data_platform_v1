#
#   Written by:  Mark W Kiehl
#   http://mechatronicsolutionsllc.com/
#   http://www.savvysolutions.info/savvycodesolutions/

# Copyright (C) Mechatroinc Solutions LLC
# License:  MIT


# configure logging
"""
import os.path
from pathlib import Path
import logging
logging.basicConfig(filename=Path(Path.cwd()).joinpath(os.path.basename(__file__).split('.')[0]+".log"), encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.info("Script start..")
"""

# Define the script version in terms of Semantic Versioning (SemVer)
# when Git or other versioning systems are not employed.
__version__ = "0.0.0"
from pathlib import Path
print("'" + Path(__file__).stem + ".py'  v" + __version__)

def savvy_get_os(verbose=False):
    """
    Returns the following OS descriptions depending on what OS the Python script is running in:
        "Windows"
        "Linux"
        "macOS"
    """

    import platform

    if platform.system() == "Windows":
        return "Windows"
    elif platform.system() == "Linux":
        return "Linux"
    elif platform.system() == "Darwin":
        return "macOS"
    else:
        raise Exception("Unknown OS: ", platform.system())


if __name__ == '__main__':
    pass

    # OS is Windows or Linux
    #from savvy_os import savvy_get_os
    print("savvy_get_os(): ", savvy_get_os())


    # ---------------------------------------------------------------------------
