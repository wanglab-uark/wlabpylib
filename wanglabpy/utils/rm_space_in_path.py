## @file
#  Change names of directories/files to remove spaces in the path
#  
#  Author: Yong Wang (c) June 2017.


import os
import sys

def print_help():
	helpmsg = '''
** Remove spaces in the names of directories/files **
Usage: 
	python rm_space_in_path.py parent_dir
Example:
	python rm_space_in_path.py ./
	python rm_space_in_path.py 
	'''
	print(helpmsg)

def rm_space_in_path(pd='./'):
    if not pd.endswith(os.sep):
        pd = pd + os.sep
    print('Checking %s' % (pd))
    fns=os.listdir(pd)
    for fn in fns:
        if not fn.startswith('.'):
            ffn = pd+fn
            nffn = ffn.replace(' ', '_')            
            if not ffn== nffn:
            	os.rename(ffn, nffn)
            	# print('%s >> %s'%(ffn, nffn))
            	ffn = nffn
            if os.path.isdir(ffn):                
                rm_space_in_path(ffn.replace(' ', '_'))
    print('Done for %s' % (pd))

if __name__ == "__main__":
    if len(sys.argv)<=1:
        print_help()        
    else:
    	if os.path.exists(sys.argv[1]):    	
    		rm_space_in_path(sys.argv[1])
    	else:
    		print('%s is not a valid path.' % argv[1])



