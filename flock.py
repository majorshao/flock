#!/usr/bin/env python -u
# encoding: utf-8


from __future__ import print_function
import time
import os
import fcntl
import errno
import sys

import argparse

class FileFlock:
   """Provides the simplest possible interface to flock-based file locking. 
   Intended for use with the `with` syntax. """

   def __init__(self, path, aString = "abcdef-123", timeout = None):
      self._path = path
      self._timeout = timeout
      self._fd = None
      self._aString = aString.strip()

   def __enter__(self):
      self._fd = os.open(self._path, os.O_APPEND | os.O_WRONLY | os.O_CREAT)
      start_lock_search = time.time()
      while True:

         time.sleep(0.1)
         print("waiting for lock.....")
         
         try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # Lock acquired!

            for i in range(0,3):
                time.sleep(0.1)
                print("holding the lock")

            os.write(self._fd, self._aString + "\n")
            return
         except (OSError, IOError) as ex:
            if ex.errno != errno.EAGAIN: # Resource temporarily unavailable
               print("Resource temporarily unavailable")
               sys.exit(1)
            elif self._timeout is not None and time.time() > (start_lock_search + self._timeout):
               # Exceeded the user-specified timeout.
               print("Exceeded the user-specified timeout.")
               sys.exit(1)


   def __exit__(self, *args):
      fcntl.flock(self._fd, fcntl.LOCK_UN)
      os.close(self._fd)
      self._fd = None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', '--file', default='.accepted', help='The file to update', required=True)
    parser.add_argument('-s', '--string', default="abcdef-123", help='The string to append to the file', required=True)
   
    args = parser.parse_args()

    updateFile = args.file
    appendString = args.string

    with FileFlock(updateFile, appendString, 3):
        print("Lock acquired.")
        
    print("Lock released.")  
    sys.exit(0) 


if __name__ == "__main__":
     main()

  



