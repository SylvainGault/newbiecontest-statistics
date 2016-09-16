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

    cur.execute("""SELECT MIN(vd.day),
                        CAST(SUM(vd.valids) AS FLOAT) * 7 /
                            (julianday('now', '-7 days', 'weekday 1', 'start of day') -
                                julianday('2006-12-11', 'weekday 1'))
            FROM (
                SELECT date(v.date) AS day, COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL AND v.date >= date('2006-12-11', 'weekday 1')
                    AND v.date < date('now', '-7 days', 'weekday 1')
                GROUP BY day
            ) AS vd
            GROUP BY strftime('%w', vd.day)
            ORDER BY day""")

    fp.write("# 0 = Sunday, 1 = Monday\n")
    fp.write("# Weekday Average-number-of-validations-that-day-of-the-week\n")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        fp.write(row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
