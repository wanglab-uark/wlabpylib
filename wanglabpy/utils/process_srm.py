## @file
#  process srm data in a folder
#  
#  Author: Yong Wang (c) Aug 2017.

import os
import sys
import getopt
import numpy
import datetime
        

def print_help():
    print('Usage: python process_srm.py hD:p:t:w:W:I:z:s:b:r:')
    print('    -h                   print this help message')
    print('    -D, --dir            directory')
    print('    -p, --pixsize        pixel size, default: 160.0')
    print('    -t, --threshold      threshold for rapidstorm, default: 4000')
    print('    -w, --psfwidthmin    min for psf width, default: 200')
    print('    -W, --psfwidthmax    max for psf width, default: 600')
    print('    -I, --psfintenmax    max for psf intensity, default: 50000')
    print('    -z, --imagesize      image size (original) in pixel, default: 256')
    print('    -s, --dcseg          segment size for drift correction, default: 1000')
    print('    -b, --dcbin          bin size for drift correct, default: 20')
    print('    -r, --concr          radius for concatenation, default: 23.55')

def logcmd(cmd):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print('[%s] %s' % (ts, cmd))
    f = open('process_srm.log','a')
    f.write('[%s] %s\n' % (ts, cmd))
    f.close()

def main(argv):
    # set default values
    pd = ''
    pixsize = 160.0
    threshold = 4000
    psfwidthmin = 200
    psfwidthmax = 600
    psfintenmax = 50000
    imagesize = 256
    dcseg = 1000
    dcbin = 20
    concr = 23.55
    
    if len(argv)<=1:
        print_help()
        return
    
    try:
        opts, args = getopt.getopt(argv,'hD:p:t:w:W:I:z:s:b:r:',
                                   ['dir=','pixsize=','threshold=','psfwidthmin=','psfwidthmax=',
                                    'psfintenmax=','imagesize=','dcseg=','dcbin=','concr='])    
    except getopt.GetoptError:
        print_help()
        return

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            return
        elif opt in ('-D', '--dir'):
            pd = arg        
        elif opt in ('-p', '--pixsize'):
            pixsize = float(arg)
        elif opt in ('-t', '--threshold'):
            threshold = int(arg)
        elif opt in ('-w', '--psfwidthmin'):
            psfwidthmin = float(arg)
        elif opt in ('-W', '--psfwidthmax'):
            psfwidthmax = float(arg)
        elif opt in ('-I', '--psfintenmax'):
            psfintenmax = float(arg)
        elif opt in ('-z', '--imagesize'):
            imagesize = int(arg)
        elif opt in ('-s', '--dcseg'):
            dcseg = int(arg)
        elif opt in ('-b', '--dcbin'):
            dcbin = int(arg)
        elif opt in ('-r', '--concr'):
            concr = float(arg)
    
    if len(pd) < 1:
        print_help()
        return

    logcmd('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
    logcmd('process_srm.py started.')
    if pd.endswith('/'):
        pd = pd[:-1]
    cmd = 'python ~/Data/pylib/rm_space_in_path.py %s' % pd
    logcmd(cmd)
    os.system(cmd)
    cmd = 'python ~/Data/pylib/run_rapidstorm.py -D %s -M %d -m %d -d 1000' % (pd, threshold, threshold)
    logcmd(cmd)
    os.system(cmd)
    locpd = '%s_th%d' % (pd, threshold)
    cmd = 'mkdir %s' % (locpd)
    logcmd(cmd)
    os.system(cmd)
    cmd = 'python ~/Data/pylib/copy_loc_files.py %s %s %d' % (pd, locpd, threshold)
    logcmd(cmd)
    os.system(cmd)
    cmd = '~/bin/matlab -nodesktop -nosplash -r "addpath(\'~/Data/matlablib/SRMC3/\'); SRMC3BatchMode(\'%s/\', %d, %f, %f, %d, %f, %d, %d, %d, %f); exit;"' % (
        locpd, threshold, psfwidthmin, psfwidthmax, psfintenmax, pixsize, imagesize, dcseg, dcbin, concr)
    logcmd(cmd)
    os.system(cmd)
    logcmd('process_srm.py finished.')
    logcmd('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n')
    

if __name__ == "__main__":
   main(sys.argv[1:])