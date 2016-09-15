#!/usr/bin/python
# coding: utf-8

import sys
import bz2
import xml.etree.cElementTree as ET
from lxml import html
import sqlite3



def printupdate(s):
    sys.stdout.write("\r" + " " * printupdate.prevlen)
    sys.stdout.write("\r" + s)
    printupdate.prevlen = len(s)
    sys.stdout.flush()

printupdate.prevlen = 0


class MinidumpCB:
    def __init__(self, cur):
        self.cur = cur
        self.state = ['']
        self.totalusers = 0


    def start(self, tag, attr):
        newstate = self.state[-1] + '.' + tag
        self.state.append(newstate)

        # The most common cases are put first so it's faster
        if newstate == ".newbiecontest.users.user.chall":
            date = attr['date']
            if date == "N/A":
                date = None

            self.cur.execute("INSERT INTO validation (userid, challid, catid, date) VALUES(?, ?, ?, ?)",
                    (self.userid, int(attr['id']), int(attr['cat']), date))

        elif newstate == ".newbiecontest.users.user":
            self.cur.execute("INSERT INTO user (nick, inscription, solvedchalls, points, lastvalidation) VALUES(?, ?, ?, ?, ?)",
                    (attr['nick'], attr['inscription'], int(attr['solvedChalls']), int(attr['points']), attr['lastValidation']))
            self.userid = self.cur.lastrowid

        elif newstate == ".newbiecontest.categories.category.challenge":
            self.cur.execute("INSERT INTO challenge (id, catid, name, creation, valids, points, score) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (int(attr['id']), self.catid, attr['name'], attr['creation'], int(attr['valids']), int(attr['points']), float(attr['score'])))

        elif newstate == ".newbiecontest.categories.category":
            self.catid = int(attr['id'])
            self.cur.execute("INSERT INTO category (id, shortname, fullname) VALUES(?, ?, ?)",
                    (self.catid, attr['short'], attr['name']))

        elif newstate == ".newbiecontest.users":
            printupdate("Importing users")

        elif newstate == ".newbiecontest.categories":
            pass

        elif newstate == ".newbiecontest":
            pass

        else:
            print "unknown tag <" + tag + ">"
            print "attrubutes: " + str(attr)
            sys.exit()



    def end(self, tag):
        laststate = self.state.pop()
        if laststate == ".newbiecontest.categories.category":
            del self.catid

        elif laststate == ".newbiecontest.users.user":
            del self.userid
            self.totalusers += 1
            if (self.totalusers % 100 == 0):
                printupdate(str(self.totalusers) + " users imported")

        elif laststate == ".newbiecontest.users":
            printupdate("Imported " + str(self.totalusers) + " users total")
            print ""


    def data(self, data):
        # No actual data
        assert data.isspace()


    def close(self):
        pass



def createtables(cur):
    printupdate("Droping old tables")
    cur.execute("DROP TABLE IF EXISTS pointstable")
    cur.execute("DROP TABLE IF EXISTS validation")
    cur.execute("DROP TABLE IF EXISTS user")
    cur.execute("DROP TABLE IF EXISTS challenge")
    cur.execute("DROP TABLE IF EXISTS category")

    printupdate("Creating new tables")
    cur.execute("""CREATE TABLE category (
        id INTEGER,
        shortname TEXT,
        fullname TEXT,
        PRIMARY KEY (id)
    )""")

    cur.execute("""CREATE TABLE challenge (
        id INTEGER,
        catid INT,
        name TEXT,
        creation TEXT,
        valids INT,
        points INT,
        score REAL,
        PRIMARY KEY (id),
        FOREIGN KEY (catid) REFERENCES category(id)
    )""")

    cur.execute("""CREATE TABLE user (
        id INTEGER,
        nick TEXT,
        inscription TEXT,
        solvedchalls INT,
        points INT,
        lastvalidation TEXT,
        PRIMARY KEY (id)
    )""")

    cur.execute("""CREATE TABLE validation (
        userid INT,
        challid INT,
        catid INT,
        date TEXT,
        PRIMARY KEY (userid, challid),
        FOREIGN KEY (challid) REFERENCES challenge(id),
        FOREIGN KEY (catid) REFERENCES category(id)
    ) WITHOUT ROWID""")

    cur.execute("""CREATE TABLE pointstable (
        minvalids INT,
        maxvalids INT,
        points INT,
        PRIMARY KEY (minvalids, maxvalids)
    ) WITHOUT ROWID""")



def createindexes(cur):
    printupdate("Creating indexes")
    cur.execute("CREATE INDEX date ON validation (date)")



def importminidump(filename, cur):
    printupdate("Importing minidump")

    fp = bz2.BZ2File(filename)
    parser = ET.XMLParser(target = MinidumpCB(cur))

    while True:
        data = fp.read(65536)
        if not data:
            break
        parser.feed(data)

    parser.close()
    fp.close()



def importpointstable(filename, cur):
    printupdate("Importing points table")

    pointstable = html.parse(filename).getroot()
    rows = pointstable.cssselect(".pointsTable tr")

    # First row contains headers
    for r in rows[1:]:
        [minvalids, maxvalids, points] = [td.text_content() for td in r.cssselect("td")]
        if not maxvalids.isdigit():
            maxvalids = 2**32 - 1
        cur.execute("INSERT INTO pointstable (minvalids, maxvalids, points) VALUES(?, ?, ?)",
                (int(minvalids), int(maxvalids), int(points)))



# Check redundancy consistency in the database
def checkdb(cur):
    printupdate("Checking database consistency")

    # Check that user.solvedchalls is the right count
    printupdate("Checking consistency of user.solvedchalls")
    cur.execute("""SELECT u.id, u.nick, u.solvedchalls, COUNT(v.challid) AS cnt
        FROM user AS u INNER JOIN validation AS v ON (u.id = v.userid)
        GROUP BY u.id, u.nick, u.solvedchalls
        HAVING u.solvedchalls != cnt LIMIT 10""")

    res = cur.fetchall()
    if len(res) != 0:
        printupdate("")
        sys.stderr.write("Inconsistent number of solved challenges for some users: " + str(res) + "\n")

    # Check that user.lastvalidation is the max validation date
    printupdate("Checking consistency of user.lastvalidation")
    cur.execute("""SELECT u.id, u.nick, u.lastvalidation, MAX(v.date) AS last
        FROM user AS u INNER JOIN validation AS v ON (u.id = v.userid)
        GROUP BY u.id, u.nick, u.lastvalidation
        HAVING ABS(strftime('%s', u.lastvalidation) - strftime('%s', last)) > 1
        ORDER BY ABS(strftime('%s', u.lastvalidation) - strftime('%s', last)) DESC LIMIT 10""")

    res = cur.fetchall()
    if len(res) != 0:
        printupdate("")
        sys.stderr.write("Inconsistent date of last validation for some users: " + str(res) + "\n")

    # Check that user.points is the sum of validation points
    printupdate("Checking consistency of user.points")
    cur.execute("""SELECT u.id, u.nick, u.points, SUM(ch.points) AS pts
        FROM user AS u INNER JOIN validation AS v ON (u.id = v.userid)
            INNER JOIN challenge AS ch ON (v.challid = ch.id)
        GROUP BY u.id, u.nick, u.points
        HAVING u.points != pts LIMIT 10""")

    res = cur.fetchall()
    if len(res) != 0:
        printupdate("")
        sys.stderr.write("Inconsistent total points for some users: " + str(res) + "\n")

    # Check that validation.catid is the right category of the challenge
    printupdate("Checking consistency of validation.catid")
    cur.execute("""SELECT v.userid, v.challid, v.catid, c.catid
        FROM validation AS v INNER JOIN challenge AS c ON (v.challid = c.id)
        WHERE v.catid != c.catid LIMIT 10""")

    res = cur.fetchall()
    if len(res) != 0:
        printupdate("")
        sys.stderr.write("Inconsistent challenge category for some validations: " + str(res) + "\n")

    # Check that challenge.valids is the total number of validations
    printupdate("Checking consistency of challenge.valids")
    cur.execute("""SELECT c.id, c.name, c.valids, COUNT(v.challid) AS vals
        FROM challenge AS c INNER JOIN validation AS v ON (c.id = v.challid)
        GROUP BY c.id, c.name, c.valids
        HAVING c.valids != vals LIMIT 10""")

    res = cur.fetchall()
    if len(res) != 0:
        printupdate("")
        sys.stderr.write("Inconsistent number of validations for some challenges: " + str(res) + "\n")

    # challenge.points w.r.t challenge.validation and the current model
    printupdate("Checking consistency of challenge.points")
    cur.execute("""SELECT c.id, c.name, c.valids, c.points, p.points
        FROM challenge AS c INNER JOIN pointstable AS p
            ON (c.valids BETWEEN p.minvalids AND p.maxvalids)
        WHERE c.points != 0 AND c.points != p.points LIMIT 10""")

    res = cur.fetchall()
    if len(res) != 0:
        printupdate("")
        sys.stderr.write("Incorrect challenge points for some challenges: " + str(res) + "\n")




def main():
    if len(sys.argv) != 4:
        print "usage: " + sys.argv[0] + " minidump.db minidump.xml.bz2 pointstable.html"

    minidumpdb = sys.argv[1]
    minidumpxmlbz2 = sys.argv[2]
    pointstablehtml = sys.argv[3]

    conn = sqlite3.connect(minidumpdb, isolation_level = "DEFERRED")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys=1")
    cur.execute("PRAGMA synchronous=off")

    createtables(cur)
    importminidump(minidumpxmlbz2, cur)
    importpointstable(pointstablehtml, cur)
    createindexes(cur)

    printupdate("Saving database")
    conn.commit()

    cur.execute("PRAGMA synchronous=full")


    checkdb(cur)
    conn.close()

    # Erase the lase message before leaving
    printupdate("")


if __name__ == '__main__':
    main()
