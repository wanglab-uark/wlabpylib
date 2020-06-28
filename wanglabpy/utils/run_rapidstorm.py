## @file
#  run rapidstorm for a folder
#  
#  Author: Yong Wang (c) June 2017.

import os
import sys
import getopt
import numpy

def single_run_rapidstorm(inputfile, pixsize=160.0, threshold=5000):
    '''
    Perform a single run on rapidstorm for inputfile
    *inputfile*
        (string) full file name, including path, of the input image. 
        It is expected that inputfile ends with '.tif'
    *pixsize*
        pixel size in nm. If the magnification is 100X, then this number should
        be 160.0 (physical pixel size on CCD is 16um).
    *threshold*
        threshold that will be used in rapidstorm.
    '''
    # base name
    basename=inputfile[:-4]+'.RapidSTORM.th'+str(threshold)
    # rapidstorm configuration filename
    configfile=inputfile[:-4]+'.RapidSTORM.th'+str(threshold)+'.config.txt'
    # cmdline
    cmdline=('rapidstorm --AmplitudeThreshold %d --AutoTerminate'
             +' --Basename %s --ChannelCount 1 --FileType TIFF'
             +' --FItWindowSize 600 --FreeSigmaFitting --InputFile "%s"'
             +' --InputMethod FileMethod --NonMaximumSuppressi 3'
             +' --OutputSigmas --PixelSizeInNM %4.1f,%4.1f'
             +' --SaveConfigFile %s --ChooseTransmission Table'
             +' --ChooseTransmission Count --Run'  
             )%(threshold, basename, inputfile, pixsize, pixsize, configfile)
    print('> single_run_rapidstorm:')
    print('>> Input      = %s'%inputfile)
    print('>> pixsize    = %4.1f'%pixsize)
    print('>> threshold  = %d'%threshold)
    
    ret = os.system(cmdline)
    if ret == 0:
        print('> Succeeded.')
        print('')
    else:
        print('> Failed.')
        print('')
    
def scan_thresholds_run_rapidstorm(inputfile, pixsize=160.0, thresholds=range(20000,1000-1,-1000)):
    for th in thresholds:
        single_run_rapidstorm(inputfile, pixsize, th)


def run_experiment(experiment, pixsize=160.0, thresholds=range(20000,1000-1,-1000)):
    # save the current folder
    currentdir=os.getcwd()
    # determine the inputfile and subfolder
    inputfile=currentdir+os.sep+experiment+os.sep+experiment+'_MMStack_Pos0.ome.tif'
    # 
    scan_thresholds_run_rapidstorm(inputfile, pixsize, thresholds)

def look_for_valid_tifs(pd='./'):    
    if not pd.endswith(os.sep):
        pd = pd + os.sep
    valid_tifs = []
    fns=os.listdir(pd)    
    for fn in fns:
       if not fn.startswith('.'):
           ffn = pd+fn
           if os.path.isdir(ffn):
               vfs = look_for_valid_tifs(ffn)
               if len(vfs) > 0:
                   for f in vfs:
                       valid_tifs.append(f)
           if os.path.isfile(ffn) and ffn.endswith('.tif'):
               if os.path.getsize(ffn) > 200*1024*1024: #> 200M
                   valid_tifs.append(ffn)
    return valid_tifs
               
    

def run_for_dir(pd='./', pixsize=160.0, thresholds=range(20000,1000-1,-1000)):
    valid_tifs = look_for_valid_tifs(pd)
    n_files = len(valid_tifs)
    n_jobs = n_files * len(thresholds)
    if n_files > 0:
        for vf in valid_tifs:
            scan_thresholds_run_rapidstorm(vf, pixsize, thresholds)
            n_jobs = n_jobs - len(thresholds)
            print('Remaining jobs = %d' % n_jobs)
        print('All calculations are done.')
    else:
        print('No calculations needed.')
        

def print_help():
    print('Usage: python run_rapidstorm.py hD:p:m:M:d:')
    print('    -h               print this help message')
    print('    -D, --dir        directory')
    print('    -p, --pixsize    pixel size, default: 160.0')
    print('    -m, --min_th     minimum threshold (included), default: 1000')
    print('    -M, --max_th     maximum threshold (included), default: 20000')
    print('    -d, --delta_th   step size for threshold, default: 1000')

def main(argv):
    # set default values
    pd = './'
    pixsize = 160.0
    min_th = 1000
    max_th = 20000
    delta_th = 1000
    
    if len(argv)<=1:
        print_help()
        return
    
    try:
        opts, args = getopt.getopt(argv,'hD:p:m:M:d:',
                                   ['dir=','pixsize=','min_th=','max_th=','delta_th='])    
    except getopt.GetoptError:
        print_help()
        return

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            return
        elif opt in ('-D', '--dir'):
            pd = arg
        elif opt in ('-m', '--min_th'):
            min_th = int(arg)
        elif opt in ('-M','--max_th'):
            max_th = int(arg)
        elif opt in ('-d', '--delta_th'):
            delta_th = numpy.abs(int(arg))
        elif opt in ('-p', '--pixsize'):
            pixsize = float(arg)
    
    print 'pd       : %s'%pd
    print 'pixsize  : %f'%pixsize
    print 'min_th   : %d'%min_th
    print 'max_th   : %d'%max_th
    print 'delta_th : %d'%delta_th
    
    ths = range(max_th, min_th-1, -delta_th)
    run_for_dir(pd, pixsize, ths)
    

if __name__ == "__main__":
   main(sys.argv[1:])