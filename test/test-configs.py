"""Module test-configs.py tests ability to import and use code in
dcfuncs/configs.py.
"""
THIS_IS = 'test-configs.py 8/18/24 D.C.'

import dcfuncs.configs as dconfigs

if __name__=='__main__':
    print(f'This is: {THIS_IS}')
    print(f'Using: {dconfigs.THIS_IS}')
    

    print('\nTesting get_configs:')
    # For this test to succeed, the directory in which this is
    # must contain the two config files test0.yaml, test1.yaml
    # and each config they specify must contain the line:
    # type: 'test-configs'
    cdicts = dconfigs.get_configs(cfiles=['test0','test1'],
                                  types=['test-configs'])
    for idict,cdict in enumerate(cdicts):
        print(f'\nReturned config {idict+1}/{len(cdicts)}:')
        print(cdict)
 
""" ************* End of module test-configs.py *****************  """
