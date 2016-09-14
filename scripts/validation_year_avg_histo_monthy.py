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

    cur.execute("""SELECT vym.month AS month, AVG(vym.valids)
            FROM (
                SELECT strftime('%m', v.date) AS month, COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL AND v.date >= '2007' AND v.date < datetime('now', 'start of month')
                GROUP BY strftime('%Y', v.date), month
            ) AS vym
            GROUP BY month
            ORDER BY month""")

    fp.write("# Month Average-number-of-validations-that-month\n")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        fp.write(row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
