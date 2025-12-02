import os
import reader

# Sets the file directory to the working directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath) 
os.chdir(dname)