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

    cur.execute("""SELECT strftime('%H:%M', vm.minuteid) AS minute,
                        SUM(CAST(vm.valids AS FLOAT) / vd.valids) /
                            (julianday('now', 'start of day') - julianday('2006-12-11'))
            FROM (
                SELECT date(v.date) AS dateid,
                    strftime('%Y-%m-%d %H:%M', v.date) AS minuteid,
                    COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL
                GROUP BY minuteid
            ) AS vm INNER JOIN (
                SELECT date(v.date) AS dateid, COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL AND v.date >= date('2006-12-11')
                    AND v.date < date()
                GROUP BY dateid
            ) AS vd USING (dateid)
            GROUP BY minute
            ORDER BY minute""")

    fp.write("# Disregard the date, only use the data marked 2000-01-02\n")
    fp.write("# Date Time Average-number-of-validations-that-time\n")

    data = cur.fetchall()
    # Ain't nobody got time fo'dat
    for date in ['2000-01-01', '2000-01-02', '2000-01-03']:
        for row in data:
            fp.write(date + " " + row[0] + " " + str(row[1]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
