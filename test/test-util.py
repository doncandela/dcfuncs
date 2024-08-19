"""Module test-util.py tests ability to import and use code in
dcfuncs/util.py.
"""
THIS_IS = 'dutil.py 8/19/24 D.C.'

import numpy as np
import dcfuncs.util as dutil

if __name__=='__main__':
    print(f'This is: {THIS_IS}')
    print(f'Using: {dutil.THIS_IS}')
    
    print('\nTesting zz:')
    # dutil.zz('util.py test code','Doing an error exit.')
    dutil.zz('util.py test code','This is just a warning.',warn=True)
    
    print('\nTesting stoi:')
    s1 = dutil.stoi('dcfuncs/util.py')
    s2 = dutil.stoi('foo')
    s3 = dutil.stoi('Have a nice day!')
    print(f'stoi results = {s1}, {s2}, {s3}')
    
    print('\nTesting get_units:')
    for x in (np.pi**10,1/575,42,45e-6):
        umult,ustr,ustrp = dutil.get_units(x)
        print(f'{x:.3e} m should be printed as {umult*x:.3f} {ustr}m'
              f' and use \'{umult*x:.3f} {ustrp+"m"}\' when plotting')

    print('\nTesting CpuTimer:')
    timer = dutil.CpuTimer('test timer',defitems=(('e4a','1e4 additions'),
                                                  ('e6a','1e6 additions')))
    a4,a6 = 0,0
    for e in range(10):
        timer.mark()
        for j in range(10_000):
            a4 += 1
        timer.mark('e4a')
        for j in range(1_000_000):
            a6 += 1
        timer.mark('e6a')
    print(f'Final values a4={a4:,.0f}  a6={a6:,.0f}')
    timer.print_times()
    
    print('\n(no test code so far for NVTI and SimArrays)')

""" ************* End of module test-util.py *****************  """
