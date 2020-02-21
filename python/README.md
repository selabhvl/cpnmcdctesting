# MCDC

**Modified Condition/Decision Coverage Library for Python**

TODO: Complete text



## Installation

This library requires Python 2.7.9 or Python 3.4+. 
If you have the python tool 'pip' installed, just download the Wheel artifact (*.whl file) 
from the Download->Artifact section in Gitlab and run:

$ pip install *.whl --user 

If you prefer to compile and install the source code by yourself, then execute the following steps. 
The dependencies of the tool are listed in requirements.txt. 
You can run the following command for installing them:

$ pip install -r requirements.txt

Afterwards you need to run:

$ python setup.py build

$ python setup.py install

for installing the library. In order to run all the tests, you must execute:

$ python setup.py test

or

$ cd Tests

$ pytest

from the root of the project folder.


For users that don’t have write permission to the global site-packages directory or 
do not want to install our library into it, Python enables the selection of the target 
installation folder with a simple option:

$ pip install -r requirements.txt --user

$ python setup.py build

$ python setup.py install --user

In Unix/Mac OS X environments:, the structure of the installation folders will be the following:

|Type of file |  Installation directory|
|------------ | --------------------------|
| modules | userbase/lib/pythonX.Y/site-packages |
| scripts | userbase/bin |
| data | userbase |
| C headers | userbase/include/pythonX.Y/distname |

And here are the values used on Windows:

| Type of file |  Installation directory |
|------------ | --------------------------|
| modules | userbase\PythonXY\site-packages |
| scripts | userbase\Scripts |
| data | userbase |
| C headers | userbase\PythonXY\Include\distname |

The advantage of using this scheme compared to the other ones described in [2] is that the 
user site-packages directory is under normal conditions always included in sys.path, which 
means that there is no additional step to perform after running the setup.py script to 
finalize the installation.

[2] Installing Python Modules (Legacy version) (https://docs.python.org/2/install/)