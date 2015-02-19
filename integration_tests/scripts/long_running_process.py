from __future__ import print_function, unicode_literals
import time
import sys
import os

def main():

    print('This is LRP', os.getpid())
    print('OK')
    sys.stdout.flush()
    for i in range(20):
        time.sleep(1)
    print('LRP is done now')
    sys.stdout.flush()

if __name__ == '__main__':
    main()
