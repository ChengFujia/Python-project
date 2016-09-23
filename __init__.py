import os

from dbdb.interface import DBDB


__all__ = ['DBDB', 'connect']


def connect(dbname):
    try:
	#Open a file in both read and write binary mod
        f = open(dbname, 'r+b')
    except IOError:
	#If not exists,create a new one
        fd = os.open(dbname, os.O_RDWR | os.O_CREAT)
        f = os.fdopen(fd, 'r+b')
    return DBDB(f)
