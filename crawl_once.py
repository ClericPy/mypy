from pytools.crawler import storage
import os

storage()
os.kill(os.getpid(),9)
