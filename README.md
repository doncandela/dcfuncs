dcfuncs/README.md 8/18/24  D.C.

Package of miscellaneous utility functions and classes, intended to be installed locally.

### HISTORY

8/18/24 First version, with code mostly copied from dem_util.py and dem_user.py in the dem21 package. 


### CONTENTS
```
dcfuncs/
   src/
      dcfuncs/         # installable package
         util.py       # utility functions: error exit, profiling, etc.
         configs.py    # reading yaml configuration files
   test/
      test-util.py
      test-configs.py
   pyproject.toml
   setup.py
```
   
### ENVIRONMENT/INSTALLATION 

Environment must have following packages installed:

   - For util.py: numpy, time
   - For configs.py: pathlib, yaml, itertools, dcfuncs (uses util.zz) 

To install dcfuncs:

   - activate desired environment
   - cd to `dcfuncs/`  (directory with `pyproject.toml`) 
   - do `$ python -m pip install -e .`
        
#### (end of README.md)

