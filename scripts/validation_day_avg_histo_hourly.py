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

    cur.execute("""SELECT strftime("%H:30", vh.hourid) AS hour,
                    CAST(SUM(vh.valids) AS FLOAT) /
                    (julianday('now', 'start of day') - julianday('2006-12-11'))
            FROM (
                SELECT strftime("%Y-%m-%d %H:30", v.date) hourid, COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL AND v.date >= '2006-12-11'
                    AND v.date < date()
                GROUP BY hourid
            ) AS vh
            GROUP BY hour
            ORDER BY hour""")

    fp.write("# Hour Average-number-of-validations-that-hour-of-the-day\n")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        fp.write(row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
