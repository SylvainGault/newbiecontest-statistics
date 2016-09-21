#!/usr/bin/python
# coding: utf-8

import sys
import sqlite3
import numpy as np


def main():
    if len(sys.argv) != 3:
        print "usage: " + sys.argv[0] + " minidump.db outputfile.data"

    minidumpdb = sys.argv[1]
    output = sys.argv[2]

    fp = open(output, 'w')
    conn = sqlite3.connect(minidumpdb, isolation_level = "DEFERRED")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=1")

    cur.execute("""SELECT date(v.date) AS day, COUNT(v.date)
            FROM validation AS v
            WHERE v.date IS NOT NULL AND v.date >= '2006-12-11' AND v.date < date()
            GROUP BY day
            ORDER BY day""")

    a = np.array([row[1] for row in cur.fetchall()], dtype = np.float)
    spec = np.fft.rfft(a)[:1:-1]
    spec = np.abs(spec)
    freq = np.fft.rfftfreq(len(a))[:1:-1]
    freq = 1.0/freq

    # We're not interested in offsets too large
    lastidx = np.searchsorted(freq, len(a) / 5)

    fp.write("# Offset Spectral-coefficient\n")
    for f, s in zip(freq[:lastidx], spec[:lastidx]):
        fp.write(str(f) + " " + str(s) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
