"""Module util.py has utility classes and functions useful for various
purposes.

Utility functions:
    zz
        Handles general error by printing a message and raising SystemExit.
        Can optionally print warning without raising SysemExit.
    stoi
        Makes an int from a string, useful for getting probably probably
        unique random seeds. 
    get_units
        Gets prefix and multiplier for printing a number in engineering units.

Classes:
    CpuTimer
        Makes a timer for code profiling.
    NTVI
        Holds variable names, types, and value infos used to set up arrays.
    SimArrays
        Uses NVTI to allocate a group of related arrays.
"""
THIS_IS = 'util.py 8/18/24 D.C.'

PREFIX = '- '   # prefix for all print statements from this module

import numpy as np
import time
        
""" ****************** UTILITY FUNCTIONS ******************** """

def zz(source,msg,warn=False):
    """Handles unrecoverable error by raising SystemExit with message on
    source and nature of problem, or issues a warning and returns.

    Parameters
    ----------
    source : str
        Name of the function that caused the error (used in exception message,
        need not be the calling function).
    msg : str
        Error message to print, typically starts with capital letter and ends
        with period.
    warn : bool
        If True will issue warning and will not raise exception.
    """
    if warn:
        print(PREFIX + f'WARNING from {source} - {msg}')
        return
    zzmsg = PREFIX + f'ERROR from {source} - {msg}'
    raise SystemExit(zzmsg)

def stoi(s):
    """Makes an int from a string, useful for getting probably unique random
    seeds by applying to strings known to be unique (e.g. name of calling
    module and function).
    """
    return sum(ord(c)*7**p for p,c in enumerate(s))

def get_units(num):
    """Gets prefix and multiplier for printing a number in engineering units.
    
    Parameters
    ----------
    num : float
        Number to be printed.
    
    Returns
    -------
    umult : float
        Number should be multiplied by mult before printing.
    ustr,ustrp : str
        String to prefix to units string. ustr uses only roman characters
        while ustr uses latex for mu (micro).
    """
    if num>1e12:
        return 1e-12,'T','T'
    elif num>1e9:
        return 1-9,'G','G'
    elif num>1e6:
        return 1e-6,'M','M'
    elif num>1e3:
        return 1e-3,'k','k'
    elif num>1.0:
        return 1.0,'',''
    elif num>1e-3:
        return 1e3,'m','m'
    elif num>1e-6:
        return 1e6,'micro-',r'$\mu$'
    elif num>1e-9:
        return 1e9,'n','n'
    else:
        return 1e12,'f','f'
    
""" ****************** UTILITY CLASSES ******************** """

class CpuTimer:
    """Makes a timer for code profiling.  Each CpuTimer keeps track of the
    cummulative cpu times (which are additive, not overlapping) for a
    set of items (but multiple CpuTimer's can be created to keep track
    of overlapping items).
    
    Current version uses time.perf_counter to get cpu time; best choice might
    depend on OS.  On Windows as of 6/2019 time.perf_counter seemed best as
    it had much better resolution than time.process_time, even though (unlike
    process_time) perf_counter includes sleep time.
    
    Parameters
    ----------
    name : str
        Name used when printing results from this timer.
    on : bool (default True)
        If False all methods return immediately doing nothing. Provided as a
        convenience to make it easy to turn off code profiling by this timer.
    defitems : list of tuple str,str (default [])
        List [(item,desc),(item,desc) of predefined items for this timer. Each
        item is a short string that is used in mark calls to mark execution
        points; desc is a longer string to describe the item in printouts.
        
    Life cycle of a CpuTimer:
        (a) mytimer=CpuTimer(...) creates the timer mytimer and effectively
        zeroes all cummulative times for this timer, calls mark to start
        timing.
        
        (b) mytimer.mark() (with no arguments) can be called any number of
        times to mark the start of a code segment to be timed by mytimer,
        which is not also the end of another segment to be timed. In this
        case time between most recent mark call (or creation of timer, if
        no previous mark call) will not be included in any timer item nor
        in total.
        
        (c) mytimer.mark(item) can be called any number of times to mark the
        end of a code segment to be timed, with the cummulative time for this
        segment labled by item.  This will also mark the start of timing for
        the immediately following code segment (nextitem) unless
        mytimer.mark() is called before a following mytimer.mark(nextitem).
        
        (d) mytimer.t(item) can be called at any point to get the cumulative
        time for a single item.
        
        (d) mytimer.ttot() can be called at any point to get the total
        cumulative time for all items.
        
        (e) mytimer.print_times() prints out all the cummulative execution
        times for the code segments defined by mytimer.mark(..) calls.
        
        (f) mytimer.zero() re-zeros the cummulative times for mytimer, then
        calls mark() to start timing.
    """
    def __init__(self,name='CpuTimer',on=True,defitems=None):
        self.off = not on
        if self.off:
            return
        self.name = name
        if defitems is None:
            self.defitems = []
        else:
            self.defitems = defitems
        self.clk = 0.0              # will hold cpu clock at most recent mark
        # Set all items to zero.
        self.ts = {}                # cumulative time for each item
        self.nests = {}             # nesting to control printing
        self.mark()                 # start timing
       
    def mark(self,item=None,nesting=None):
        """Mark the end time for a code segment being timed; also marks the
        start time for the next code segment.
        
        Parameters
        ----------
        item : str or None
            Name for the timed code segment ended by this mark call, and the
            start of the next timed code segment.  If item=None only marks
            the start of the next segment.
            
            item can match one of the items in defitems supplied to __init__,
            or not.  This only affects how the item is printed by print_times.
        nesting : str
            If supplied on first mark call for an item not in defitems,
            controls print order and indenting for this item.  Items will be
            printed in alphabetical order of nesting, with one indent for
            every '.' in nesting.
            
        Following scheme gives a nice printout using nesting for items not in
        defitems.  Here functiona and its helper functionb are profiled:
        ::
            # Code calling functiona:
            timer.mark()
            functiona(...)
            timer.mark('functiona end','99')
            
            # Inside functiona:
            def functiona(...):
                timer.mark('functiona start','0')
                astuff1()
                timer.mark('astuff1','1')
                functionb()
                timer.mark('functionb end','2.99')
                astuff3()
                timer.mark('astuff3','3')
                return
                
            # Inside functionb:
            def functionb(...):
                timer.mark('functionb start','2')
                bstuff1()
                timer.mark('bstuff1','2.1')
                bstuff2()
                timer.mark('bstuff2','2.2')
                return
                
            # The printed output from print_times will be:
            #
            #   Total time for name: 1001.00s
            #  0 functiona start        0.01s,   0.0% of total
            #  1 astuff1                5.35s,   0.5% of total
            #  2 functionb start        0.02s,   0.0% of total
            #     2.1 bstuff1          14.34s,   1.4% of total
            #     2.2 bstuff2          23.44s,   2.3% of total
            #     2.99 functionb end    0.01s,   0.0% of total
            #  3 astuff3              9952.03s, 99.5% of total
        This scheme captures all of the time used including time to call the
        functions (in the 'start' items) and to return from them (in the'end'
        items).
        """
        if self.off:
            return
        clk0 = self.clk                   # cpu clock time at last mark (s)
        self.clk = time.perf_counter()    # current cpu clock time (s)
        # self.clk = time.perf_counter()  # uncomment to see how long takes
        if not item:
            return                        # not marking end of an interval
        dt = self.clk - clk0              # time used since last mark
        try:
            self.ts[item] += dt           # add to cum time for this item
        except KeyError:
            self.ts[item] = dt            # start a new item
            self.nests[item] = nesting

    def t(self,item):
        """Get time for a single item.
        
        Parameters
        ----------
        item : str
            The item for which cummulative time is requested.
        
        Returns
        -------
        t : float
            Cummulative time for item (s), or 0.0 if this item has not been
            marked.
        """
        if self.off:
            return 0.0
        return self.ts.get(item,0.0)

    def ttot(self):
        """Returns the total cumulative time for all items.  Does not reset
        cummulative times.
        
        Returns
        -------
        t : float
            Total cumulative time (s) for all items for which mark has been
            called, up to the time of the most recent mark call.
        """
        if self.off:
            return 0.0
        return sum(self.ts[j] for j in self.ts)

    def print_times(self):
        """Print out the total time for all items and individual item times.
        The predefined items are printed first, in the order they were given
        in defitems when this CpuTimer was initialized. Additional items not
        in defitems are printed in order and with indentation controlled by
        the argument nesting supplied to mark.
        """
        if self.off:
            return
        # Print header with name and total time for all items.
        ttot = sum(self.ts[j] for j in self.ts)
        print(PREFIX + 70*'-')
        print(PREFIX + f'{f"Total time for {self.name}":>37}{ttot:11,.3f}s'
                       f' = {ttot/3600:,.3f}h')
        # Print out timings of predefined items, if profiled.
        for item,desc in self.defitems:
            if item in self.ts:
                t = self.ts[item]
                self.print_times1(desc,t,ttot)
        # Get list of additional items profiled.
        additems = [item for item in self.ts
                    if not item in [item for item,desc in self.defitems]]
        # Directly print items without nesting, and build list nestitems =
        # [(nesting,desc,t),(nesting,des,t)..] of items with nesting.
        nestitems = []
        for item in additems:
            desc = item
            t = self.ts[item]
            nesting = self.nests[item]
            if nesting:
                nestitems.append((nesting,desc,t))
            else:
                self.print_times1(desc,t,ttot)
        # Process the list of nested items then print from processed list.
        nestitems2 = self.print_times2(nestitems)
        for desc2,t in nestitems2:
            self.print_times1(desc2,t,ttot,True)
        print(PREFIX + 70*'-',flush=True)

    def print_times1(self,desc,t,ttot,ljust=False):
        """Helper for print_times: prints one item, left-justified if
        ljust=True.
        """
        tpct = 100*t/max(ttot,1e-10)  # avoid div by 0 if ttot=0
        if ljust:
            print(PREFIX + f'{" ":7}{desc:.<30}{t:>11,.3f}s,'
                  f' {tpct:>4.1f}% of total')
        else:
            print(PREFIX + f'{desc:>37}{t:>11,.3f}s, {tpct:>4.1f}% of total')

    def print_times2(self,nestitems):
        """Helper for print_times: Builds ordered, indented list of the items
        with nesting supplied.
        
        Parameters
        ----------
        nestitems : list of tuple str,str,float
            [(nesting,desc,t),(nesting,desc,t)..] with nesting and desc as
            supplied to mark.
            
        Returns
        -------
        nestietms2 : list of tuple str,float
            [(desc2,t),(desc2,t)...] ordered according to the the nesting
            and with descriptions incorporating indentation and nesting.
        """
        # Build unsorted output list keeping nesting as first element.
        nestitems1 = []
        for nesting,desc,t in nestitems:
            # Build desc 2 adding an indent for every '.' in nesting.
            desc2 = nesting.count('.')*'   ' + nesting + ' ' + desc
            nestitems1.append((nesting,desc2,t))
        # Alphabetize according to nesting:
        nestitems1.sort(key=lambda x : x[0])
        # Strip nesting to get final output list.
        nestitems2 = [(desc2,t) for _,desc2,t in nestitems1]
        return nestitems2
        
    def zero(self):
        """Reset all cummulative times for this timer to zero.
        """
        self.ts = {}                # cumulative time for each item
        self.nests = {}             # nesting to control printing
        self.mark()                 # start timing

class NTVI():
    """Utility object to hold information used to set up arrays for
    vectorized calculations.
    
    Parameters
    ----------
    names : list of str (optional)
        Name of each variable to be allocated.
    etypes : list of type (optional)
        Type of the elements of each variable. Must be same length as names.
    vals : list (optional)           
        Value of each variable = scalar, list or array of corresponding
        type in etypes.  For some uses of NTVI these are actual values,
        while for other uses these are sample values used to convey the
        shapes of arrays to be allocated. Must be same length as names.
    infos : list of str (optional)
        Information strings on the computed values suitable for printing.
        Length need not match that of the other lists.
    """
    def __init__(self,names=None,etypes=None,vals=None,infos=None):
        if names is None:
            self.names = []
            self.etypes = []
            self.vals = []
        else:
            self.names = names
            self.etypes = etypes
            self.vals = vals
        if infos is None:
            self.infos = []
        else:
            self.infos = infos
        
    def val(self,name):
        """Returns value corresponding to name, or None is name is not
        in self.names."""
        try:
            return self.vals[self.names.index(name)]
        except ValueError:
            return None

    def replaceval(self,name,newval):
        """Replace value corresponding to name with new value."""
        self.vals[self.names.index(name)] = newval
        
    def insertval(self,name,etype,val,index=-1,info=None):
        """Inserts new name,etype,val,info (optional) at location index in
        lists. index=0 to insert at start, -1 (def) to insert at end."""
        self.names.insert(index,name)
        self.etypes.insert(index,etype)
        self.vals.insert(index,val)
        if info is not None:
            self.infos.insert(index,info)

    def merge(self,ntvi2):
        """Appends the names, types, values, and infos in ntvi2 to this
        object. ntvi2 can also be None indicating nothing to be appended.
        """
        if ntvi2 is None:
            return
        self.names += ntvi2.names
        self.etypes += ntvi2.etypes
        self.vals += ntvi2.vals
        self.infos += ntvi2.infos
        
    def copy(self):
        """Returns a copy of this object."""
        return NTVI(self.names.copy(),self.etypes.copy(),
                    self.vals.copy(),self.infos.copy())

class SimArrays:
    """Utility object that allocates a group of arrays for vectorized
    calculations, and optionally fills the arrays with values. Was
    written for DEM simulation code to facilitate logical grouping of
    arrays of different types and shapes.

    The arrays in one SimArrays object will all pertain to one sort of
    thing (eg grain types, or grains that are present), and initially the
    arrays in a SimArrays will all have the same number of rows (first
    dimension, eg number of grain types, or number of grains present). A
    subset of the arrays can be extended to have more rows by calling
    SimArrays.extend.
    
    There are three different ways to initialize a SimArrays:
        1. The arrays can be initialized to all zeros by providing the number
        of rows in the argument zrows. In this case ntvis should have a single
        element, which describes the arrays to be created, and vlists should
        not be provided.
        
        2. The arrays can be initialized to specified values by providing a
        list of NTVIs in ntvis.  The number of rows will equal the length
        of this list, and the values used to initialize  the arrays will
        be taken from the values in the ntvis.  Neither zrows nor vlists
        should be provided.
        
        3. The arrays can be initialized to specified values by providing
        the values in vlists. In this case ntvis should have a single element,
        which describes the arrays to be created, and zrows should not be
        provided.  
    In all cases the shape of the c'th array will be (rows,) prepended to the
    shape of the c'th element of ntvis[0].vals, with rows given by
        1. rows=zrows if zrows is provided (zero-filled SimArrays), or
        
        2. rows=len(ntvis) if neither zrows nor vlists is provided (SimArrays
        filled with values from ntvis), or
        
        3. rows=the length of the longest concatenation in vlists if vlists
        is provided (SimArrays filled with values from vlists)

    Parameters
    ----------
    ntvis : list of NTVI
        If an empty list, this object returns allocating no arrays. Otherwise
        ntvis[0] determines the names, element types, and shapes of each
        row of the arrays allocated.
        
        If neither zrows nor vlists is provided, ntvis[r].vals additionally
        specifies the values used to intialize row r of the arrays. In this
        case the arrays will be initialialized by copying ntvis[r].vals[c]
        into the rth row of the c'th array.
    zrows : int (optional)
        If provided, number of rows in each array.  In this case the arrays
        will be initialized with zeros.
    vlists : list of list of array (optional)
        If provided, gives values that will be filled into some or all of the
        arrays.  The values put into the c'th array (specified by
        ntvis[0].names[c], etc) are determined by vlists[c].
    
        If the length of vlists is less than c or vlists[c]=[], the c'th array
        will be initialized to zeros.
        
        Otherwise, vlists[c] should be a list of arrays.  These arrays will
        be concatenated and copied into the c'th array (or the beginning part
        of the c'th array if the length of the concenation is less than the
        number of rows).
    
        The number of rows will be the length of the longest such
        concatentation in vlists, which must be at least 1.
    ntvis must always have at least one element, and only one of zrows, vlists
    should be provided.
    """
    def __init__(self,ntvis,zrows=None,vlists=None):
        if not len(ntvis):
            self.ntvi0 = None
            return        
        self.ntvi0 = ntvis[0]  # will determine types and shapes of the arrays

        # Find number of rows in the arrays.
        if zrows is not None:
            rows = zrows          # leaving arrays zero-filled
        elif vlists is None:
            rows = len(ntvis)     # filling array values from ntvis
        else:
            # Filling array values from vlists, find max len of concats.
            rows = max(sum(len(a) for a in vl) for vl in vlists)
        self.rows = rows   # save for use by extend

        # Allocate the arrays.
        for c,name in enumerate(self.ntvi0.names):
            shape = (rows,)+np.shape(self.ntvi0.vals[c])  # shape of array
            etype = self.ntvi0.etypes[c]                  # type of elements
            # Uncomment to see when and what size arrays are being allocated.
            # print(f'SimArrays.__init__: shape={shape} etype={etype}')
            setattr(self,name,np.zeros(shape,etype))

        # Fill array values as needed.
        if zrows is not None:
            return                # leave arrays zero-filled
        elif vlists is None:
            # Copy values from ntvis into the arrays.
            for c,name in enumerate(ntvis[0].names):
                array = getattr(self,name)
                for r in range(rows):
                    array[r] = ntvis[r].vals[c]
            return
        else:
            # Fill array values from vlists
            for c,name in enumerate(ntvis[0].names):
                array = getattr(self,name)
                if len(vlists)>c:      # if not past end of vlists...
                    if len(vlists[c]): # ..and this element of vlists non-empty
                        # Concatenate the arrays in this element of vlists to
                        # get values to put in c'th output array.
                        ac = np.concatenate(vlists[c])
                        array[0:len(ac)] = ac

    def extend(self,names,erows):
        """Reallocate some of the arrays to have more than the original
        number of rows (number of rows when this SimArrays was initialized).
        Current values within the original number of rows will be copied into
        the extended array, while elements of the extended array beyond the
        original number of arrays will be set to zero.
        
        Parameters
        ----------
        names : list of str
            Which arrays should be extended.
        ewrows : int
            Extended number of rows for arrays that will be extended, must be
            >= original number of rows.
        """
        if erows<self.rows:
            zz('extend','New number of rows erows is less than original num.')
        ntvi0 = self.ntvi0
        for c,name in enumerate(ntvi0.names):
            if name in names:
                array = getattr(self,name)
                newshape = (erows,)+np.shape(ntvi0.vals[c])   # extended shape
                etype = ntvi0.etypes[c]                       # element type
                newarray = np.zeros(newshape,etype)
                # Copy self.rows rows from old array to new array.
                newarray[0:self.rows] = array[0:self.rows]
                setattr(self,name,newarray)

""" ****************** TEST CODE ******************** """
if __name__=='__main__':
    print(f'This is: {THIS_IS}')
    
    print('\nTesting zz:')
    # zz('util.py test code','Doing an error exit.')
    zz('util.py test code','This is just a warning.',warn=True)
    
    print('\nTesting stoi:')
    s1 = stoi('dcfuncs/util.py')
    s2 = stoi('foo')
    s3 = stoi('Have a nice day!')
    print(f'stoi results = {s1}, {s2}, {s3}')
    
    print('\nTesting get_units:')
    for x in (np.pi**10,1/575,42,45e-6):
        umult,ustr,ustrp = get_units(x)
        print(f'{x:.3e} m should be printed as {umult*x:.3f} {ustr}m'
              f' and use \'{umult*x:.3f} {ustrp+"m"}\' when plotting')

    print('\nTesting CpuTimer:')
    timer = CpuTimer('test timer',defitems=(('e4a','1e4 additions'),
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

""" ************* End of module util.py *****************  """
