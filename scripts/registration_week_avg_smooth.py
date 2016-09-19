#!/usr/bin/python
# coding: utf-8

import sys
import sqlite3
import datetime


def main():
    if len(sys.argv) != 3:
        print "usage: " + sys.argv[0] + " minidump.db outputfile.data"

    minidumpdb = sys.argv[1]
    output = sys.argv[2]

    fp = open(output, 'w')
    conn = sqlite3.connect(minidumpdb, isolation_level = "DEFERRED")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=1")

    cur.execute("""SELECT date('2006-12-11', 'weekday ' || strftime('%w', uh.hourid)) AS day,
                        strftime('%H:30', uh.hourid) AS hour,
                        SUM(CAST(uh.regs AS FLOAT) / uw.regs) * 7 /
                            (julianday('now', '-7 days', 'weekday 1', 'start of day') -
                                julianday('2006-12-10', 'weekday 1'))
            FROM (
                SELECT date(u.inscription, 'weekday 0') AS weekid,
                    strftime('%Y-%m-%d %H:30', u.inscription) AS hourid,
                    COUNT(u.inscription) AS regs
                FROM user AS u
                WHERE u.inscription IS NOT NULL
                GROUP BY hourid
            ) AS uh INNER JOIN (
                SELECT date(u.inscription, 'weekday 0') AS weekid, COUNT(u.inscription) AS regs
                FROM user AS u
                WHERE u.inscription IS NOT NULL AND u.inscription >= date('2006-12-10', 'weekday 1')
                    AND u.inscription < date('now', '-7 days', 'weekday 1')
                GROUP BY weekid
            ) AS uw USING (weekid)
            GROUP BY day, hour
            ORDER BY day, hour""")

    fp.write("# Disregard the actual date, only its day-of-the-week that matters\n")
    fp.write("# Data has been repeated 3 times for kdensity to work properly\n")
    fp.write("# only the week from 2006-12-11 00:00 to 2006-12-18 00:00 should be plotted\n")
    fp.write("# Date Average-number-of-validations-that-hour-in-week\n")

    data = cur.fetchall()
    for offset in [-1, 0, 1]:
        weekoffset = datetime.timedelta(weeks = offset)
        for row in data:
            date = datetime.date(*[int(a) for a in row[0].split('-')])
            date += weekoffset
            fp.write(str(date) + " " + row[1] + " " + str(row[2]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
