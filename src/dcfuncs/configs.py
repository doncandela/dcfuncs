"""Module dcfuncs/configs.py has code to read .yaml configuration files into
nested dicts. Features:
    (a) Can check that config files are of specified 'types' i.e. intended for
    the reading program.
    
    (b) Can read a sequence of config files, with the later files modifying
    matching items in the earlier files while leaving other items unchanged.
    
    (c) Can use the multi-document feature of yaml to read multiple configs
    from a single config file, and when more than one multiple-doc yaml
    files are specified will generate all combos of the configs from each
    yaml file.

Functions:
    get_configs
        Reads yaml configuration files and returns dicts based on their
        contents.
"""
THIS_IS = 'configs.py 8/18/24 D.C.'

PREFIX = '- '   # prefix for all print statements from this module

from pathlib import Path
import yaml,itertools
import dcfuncs.util as dutil

""" ****************** UTILITY FUNCTIONS ******************** """

def get_configs(cfiles=[],types=[],verbose=1):
    """Reads yaml configuration files and returns dicts based on their
    contents. '.yaml' is appended to each provided file name before it is
    opened. Each successive .yaml file adds to (and overrides) settings from
    earlier files. This works on dicts nested to any level. Thus for example
        getconfigs(cfiles=[defaults]+sys.argv[1:])
    will first parse defaults.yaml (which could hold and document default
    configuration settings), then successivly override the defaults based on
    one or more configuration file names supplied (without .yaml suffix) on
    the command line.
    
    A .yaml file that contains D>1 documents (as delimted by --- lines) will
    multiply the number of dicts in the output by D.  So a .yaml file with D=2
    followed by a .yaml file with D=3 will result in 6 dicts in the return
    from this function with all possible combinations from the two files.
    
    Parameters
    ----------
    cfiles : list of str or Path (default [])
        Names of files (without '.yaml' suffixes) to be parsed.
    types : list (default [])
        If not [] will check that each returned dict has an entry 'type'
        equal to an element of types, if not will do error exit.
    verbose : int
        Controls printing:
            0 - print nothing
            1 - print one line giving number of configs and files used
            2 - also print dicts being returned
        
    Returns
    -------
    cdicts : list of dicts
        List of dicts of config values, one dict for each combination of
        documents in the .yaml files.
    """
    def rupdate(dict1,dict2):
        """Helper: Returns a copy of dict1 recursively updated by dict2."""
        dict1c = dict1.copy()
        for key,val in dict2.items():
            if isinstance(val,dict):
                dict1c[key] = rupdate(dict1c.get(key,{}),val)
            else:
                dict1c[key] = val
        return dict1c   
    def finaldict(dicts):
        """Successively update an intially empty dict with the members
        of the input list of dicts."""
        fd = {}
        for d in dicts:
            fd = rupdate(fd,d)
        return fd
    # Make list of all the .yaml files to be read.
    files = [Path(cfile).with_suffix('.yaml') for cfile in cfiles]
    # Read and parse the .yaml files into a list of lists, with each sublist
    # a list the dicts specified by the documents in one .yaml file.
    fdicts = []
    for file in files:
        with open(file) as strm:
            fdicts.append([*yaml.safe_load_all(strm)])
    # Use itertools.product to form all combinations of the documents in the
    # input files, and use finaldict to convert each combination to an output
    # dict by succsessivly updating an initially empty dict.
    cdicts = [finaldict(combo) for combo in itertools.product(*fdicts)]
    nd = len(cdicts)
    if verbose>=1:
        filestrs = [str(file) for file in files]
        print(PREFIX + f'Read {nd} config(s) from {" << ".join(filestrs)}')
    if verbose>=2:
        for ic,c in enumerate(cdicts):
            print(PREFIX + f'CONFIG {ic+1}/{nd}:\n{c}')
    if types:
        for cdict in cdicts:
            if not cdict.get('type') in types:
                dutil.zz('getconfigs','Config file does not have type'
                   f' in allowed types {types}.')
    return cdicts

""" ****************** TEST CODE ******************** """
if __name__=='__main__':
    print(f'This is: {THIS_IS}')
    print(f'Using: {dutil.THIS_IS}')

    print('\nTesting get_configs:')
    # For this test to succeed, the directory in which this is
    # must contain the two config files test0.yaml, test1.yaml
    # and each config they specify must contain the line:
    # type: test-yaml
    cdicts = get_configs(cfiles=['test0','test1'],types=['test-configs'])
    for idict,cdict in enumerate(cdicts):
        print(f'\nReturned config {idict+1}/{len(cdicts)}:')
        print(cdict)
    
""" ************* End of module configs.py *****************  """
