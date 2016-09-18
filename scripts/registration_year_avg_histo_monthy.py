#!/usr/bin/python
# coding: utf-8

import sys
import sqlite3


def main():
    if len(sys.argv) != 3:
        print "usage: " + sys.argv[0] + " minidump.db outputfile.data"

    minidumpdb = sys.argv[1]
    output = sys.argv[2]

    fp = open(output, 'w')
    conn = sqlite3.connect(minidumpdb, isolation_level = "DEFERRED")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=1")

    cur.execute("""SELECT rym.month AS month, AVG(rym.regs)
            FROM (
                SELECT strftime('%m', u.inscription) AS month, COUNT(u.id) AS regs
                FROM user AS u
                WHERE u.inscription IS NOT NULL AND u.inscription >= '2007'
                AND u.inscription < date('now', 'start of month')
                GROUP BY strftime('%Y', u.inscription), month
            ) AS rym
            GROUP BY month
            ORDER BY month""")

    fp.write("# Month Average-number-of-registration-that-month\n")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        fp.write(row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
