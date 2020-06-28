## @file
#  copy localization files 
#  
#  Author: Yong Wang (c) June 2017.

import os
import sys
import getopt
import numpy

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

def copy_loc_files(source_dir, dest_dir, threshold):
    if not source_dir.endswith(os.sep):
        source_dir = source_dir + os.sep
    if not dest_dir.endswith(os.sep):
        dest_dir = dest_dir + os.sep
    # 
    valid_tifs = look_for_valid_tifs(source_dir)
    cnt = 0
    for vf in valid_tifs:        
        locfn = vf[:-3]+'RapidSTORM.th'+str(threshold)+'.txt'
        if os.path.exists(locfn):
            print('Copying %s...'%locfn)
            newlocfn = locfn.replace('/', '_')
            dfn = dest_dir+newlocfn
            to_copy = True
            if os.path.exists(dfn):
              info_old = os.stat(locfn)
              info_new = os.stat(dfn)
              if info_old.st_size == info_new.st_size:
                to_copy = False
                print('\tSkiped.')
            if to_copy:
              os.system('cp '+locfn+' '+dfn)
              cnt = cnt+1
              print('\tCopied.')
    print('Copied %d files.' % cnt)
    sys.stdout.flush()


        

def print_help():
    print('Usage: python copy_loc_files.py source_dir dest_dir threshold')
    
if __name__ == "__main__":
    if len(sys.argv)==4:
        source_dir = sys.argv[1]
        dest_dir = sys.argv[2]
        threshold = int(sys.argv[3])
        copy_loc_files(source_dir, dest_dir, threshold)
    else:
        print_help()
