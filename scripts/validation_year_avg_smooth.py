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

    cur.execute("""SELECT vd.day AS day,
                        SUM(CAST(vd.valids AS FLOAT) / vy.valids) /
                            (strftime('%Y') - 2007)
            FROM (
                SELECT strftime('%Y', v.date) AS year,
                        strftime('%m-%d', v.date) AS day,
                        COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL
                GROUP BY year, day
            ) AS vd INNER JOIN (
                SELECT strftime('%Y', v.date) AS year, COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL AND year > '2006' AND year < strftime('%Y')
                GROUP BY year
            ) AS vy USING (year)
            GROUP BY day
            ORDER BY day""")

    fp.write("# Disregard the year in the date and only use the data for 2000\n")
    fp.write("# Date Average-number-of-validations-that-day\n")

    data = cur.fetchall()

    for year in ["1999", "2000", "2001"]:
        for row in data:
            fp.write(year + "-" + row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
