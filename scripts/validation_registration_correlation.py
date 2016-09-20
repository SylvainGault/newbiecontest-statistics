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

    cur.execute("""SELECT vd.day, vd.valids, ud.regs
            FROM (
                SELECT date(v.date) AS day,
                        COUNT(v.date) AS valids
                FROM validation AS v
                WHERE v.date IS NOT NULL
                GROUP BY day
            ) AS vd INNER JOIN (
                SELECT date(u.inscription) AS day,
                        COUNT(u.id) AS regs
                FROM user AS u
                WHERE u.inscription IS NOT NULL
                GROUP BY day
            ) AS ud USING (day)""")

    fp.write("# Date Number-of-validations Number-of-registrations\n")
    while True:
        row = cur.fetchone()
        if row is None:
            break
        fp.write(row[0] + " " + str(row[1]) + " " + str(row[2]) + "\n")

    conn.close()
    fp.close()


if __name__ == '__main__':
    main()
