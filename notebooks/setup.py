import sys
import os

modules_path = os.path.realpath('../src')
sys.path.append(modules_path)
os.chdir(os.path.realpath('..'))