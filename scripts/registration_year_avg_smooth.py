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

    cur.execute("""SELECT ud.day AS day,
                        SUM(CAST(ud.regs AS FLOAT) / uy.regs) /
                            (strftime('%Y') - 2007)
            FROM (
                SELECT strftime('%Y', u.inscription) AS year,
                        strftime('%m-%d', u.inscription) AS day,
                        COUNT(u.id) AS regs
                FROM user AS u
                WHERE u.inscription IS NOT NULL
                GROUP BY year, day
            ) AS ud INNER JOIN (
                SELECT strftime('%Y', u.inscription) AS year,
                        COUNT(u.inscription) AS regs
                FROM user AS u
                WHERE u.inscription IS NOT NULL AND
                        year > '2006' AND year < strftime('%Y')
                GROUP BY year
            ) AS uy USING (year)
            GROUP BY day
            ORDER BY day""")

    fp.write("# Disregard the year in the date and only use the data for 2000\n")
    fp.write("# Date Average-number-of-registrations-that-day\n")

    data = cur.fetchall()

    for year in ["1999", "2000", "2001"]:
        for row in data:
            fp.write(year + "-" + row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
