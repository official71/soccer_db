#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, flash
import re
import urllib


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
# DATABASEURI = "postgresql://user:password@104.196.18.7/w4111"
DATABASEURI = "postgresql://yq2211:1505@35.185.80.252/w4111"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

DIR_TEAM_IMAGES = 'static/images/teams/'
DIR_LEAGUE_IMAGES = 'static/images/leagues/'

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

def checked(x):
    return x if not x is None else '-'

def chknull(x):
    return x if x else ''

def add_where_clause(where, add):
    if len(where) > 0:
        return "{} AND {}".format(where, add)
    else:
        return " WHERE {}".format(add)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/teams', methods=['GET'])
def teams():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # get the enum of countries for 'select' when filtering teams
    cursor = g.conn.execute("SELECT country FROM teams GROUP BY country ORDER BY country")
    countries = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # get the enum of stadiums for 'select' when adding a team
    cursor = g.conn.execute("SELECT name,country,city FROM stadiums ORDER BY country,name")
    stadiums = [dict(name=row[0],country=checked(row[1]),
        city=checked(row[2])) for row in cursor.fetchall()]
    cursor.close()

    # parse filters
    filter_country = request.args.get('filter_country')
    sort_by = request.args.get('sort_by')

    sqlcmd = "SELECT tid,name,logo,country,year_founded FROM teams"
    if not filter_country is None and not filter_country == 'All':
        sqlcmd += add_where_clause("", "country='{}'".format(filter_country))
    if not sort_by is None:
        if sort_by == '-':
            pass
        elif sort_by == 'Name A-Z':
            sqlcmd += " ORDER BY name"
        elif sort_by == 'Name Z-A':
            sqlcmd += " ORDER BY name DESC"
        elif sort_by == 'Country':
            sqlcmd += " ORDER BY country,name"
        elif sort_by == 'Year founded':
            sqlcmd += " ORDER BY year_founded"

    cursor = g.conn.execute(sqlcmd)
    fetchall = cursor.fetchall()
    teams = [dict(ind=i+1, tid=row[0], name=row[1], 
        logo=DIR_TEAM_IMAGES+row[2], country=row[3], 
        year=checked(row[4])) for (i, row) in zip(xrange(len(fetchall)), fetchall)]
    cursor.close()
    
    return render_template("teams.html", teams=teams, 
        countries=countries, stadiums=stadiums)

@app.route('/teams', methods=['POST'])
def add_team():
    name = chknull(request.form.get('add_name'))
    country = chknull(request.form.get('add_country'))
    year = chknull(request.form.get('add_year'))
    logo_url = request.form.get('add_logo')
    stadium = request.form.get('add_stadium')
    
    sname = ''
    scountry = ''
    if stadium:
        # "Emirates Stadium - (England, London)" parsing
        rs = re.search(r'(?P<sname>.+) - \((?P<scountry>.+), (?P<scity>.+)\)', stadium)
        if rs:
            sname = rs.group('sname')
            scountry = rs.group('scountry')        

    # retrieve the logo image from url 
    # e.g. https://upload.wikimedia.org/wikipedia/en/thumb/d/d2/Juventus_Turin.svg/150px-Juventus_Turin.svg.png
    fname = ''
    if logo_url:
        try:
            fname = "{}.{}".format(
                re.sub(r'[^a-z_]', '' ,re.sub(r' ', '_', name.lower())), 
                logo_url.split('.')[-1])
            urllib.urlretrieve(logo_url, DIR_TEAM_IMAGES + fname)
        except Exception as e:
            print("Error processing image URL:\n{}\n".format(e))

    print("Adding new team:{}, country:{}, year:{}, stadium:{}({}), logo:{}".format(
        name, country, year, sname, scountry, fname))

    sqlcmd = "INSERT INTO teams (name,logo,year_founded,country,stadium) \
        VALUES ('{}','{}',{},'{}',(SELECT sid FROM stadiums WHERE name='{}' AND country='{}'))".format(
        name, fname, year, country, sname, scountry)
    
    try:
        g.conn.execute(sqlcmd)
    except Exception as e:
        print("Error executing SQL command:\n{}\n".format(e))

    return redirect('/teams')

@app.route('/delete_team', methods=['POST'])
def del_team():
    select = request.form.get('delete_team')
    if select is None:
        abort(400)

    name = ""
    country = ""
    if select and not select == '-':
        rs = re.search(r'(?P<name>.+) - \((?P<country>.+)\)', select)
        if rs:
            name = rs.group('name')
            country = rs.group('country')
    if not name or not country:
        return redirect('/teams')

    print("Deleting team:{}, country:{}".format(name, country))

    sqlcmd = "DELETE FROM teams WHERE name='{}' AND country='{}'".format(
        name, country)

    try:
        g.conn.execute(sqlcmd)
    except Exception as e:
        print("Error executing SQL command:\n{}\n".format(e))

    return redirect('/teams')


@app.route('/team', methods=['GET'])
def team():
    # DEBUG: this is debugging code to see what request looks like
    # print request.args

    tid = request.args.get('tid')
    if tid is None:
        abort(400)

    sqlcmd = "SELECT name,logo,country,year_founded,theme_color,stadium FROM teams WHERE tid='{}'".format(tid)
    cursor = g.conn.execute(sqlcmd)
    row = cursor.fetchone()
    cursor.close()
    team = dict(tid=tid, name=row[0], logo=DIR_TEAM_IMAGES+row[1], 
        country=row[2], year=row[3])
    stadium_id = row[5]

    # continue to fetch stadium info
    if not stadium_id is None:
        sqlcmd = "SELECT name FROM stadiums WHERE sid={}".format(stadium_id)
        cursor = g.conn.execute(sqlcmd)
        stadium = dict(id=stadium_id, name=cursor.fetchone()[0])
        cursor.close()
    else:
        stadium = {}

    # continue to fetch rivary clubs
    sqlcmd = "SELECT t.name AS rtname,rt.rtid,rt.name \
        FROM teams t JOIN\
        (SELECT tid2 AS rtid,name FROM rivaries WHERE tid1={} \
        UNION SELECT tid1 AS rtid,name FROM rivaries WHERE tid2={}) AS rt \
        ON t.tid=rt.rtid".format(tid, tid)
    cursor = g.conn.execute(sqlcmd)
    rivaries = [dict(tname=row[0], tid=row[1], 
        name=checked(row[2])) for row in cursor.fetchall()]
    cursor.close()

    # continue to fetch all the history coaches
    sqlcmd = "SELECT c.cid,p.first_name || ' ' ||p.last_name AS name, \
        cw.year_begin,cw.year_end,cw.role,cw.sacked,cw.percent_win \
        FROM coaches c,people p,coach_works cw \
        WHERE cw.tid={} AND cw.cid=c.cid AND c.pid=p.pid \
        ORDER BY cw.year_begin,cw.role".format(tid)
    cursor = g.conn.execute(sqlcmd)
    coaches = []
    for row in cursor.fetchall():
        dd = dict(id=row[0], name=row[1], yr_beg=row[2], role=row[4])
        dd['pwin'] = checked(row[6])
        yr_end = row[3]
        if yr_end is None:
            yr_end = '-'
        elif row[5]:
            yr_end = str(yr_end) + " (sacked)"
        dd['yr_end'] = yr_end
        coaches.append(dd)
    cursor.close()

    # continue to fetch the standing info of the team
    sqlcmd = "SELECT ss.sid,l.lid,ss.year_begin,ss.year_end,l.name,l.logo \
        FROM standing sd,seasons ss,leagues l \
        WHERE sd.team={} AND sd.season=ss.sid AND sd.league=l.lid \
        ORDER BY ss.year_begin DESC".format(tid)
    cursor = g.conn.execute(sqlcmd)
    standing = [dict(sid=row[0], lid=row[1], yr_beg=row[2], 
        yr_end=row[3], lname=row[4], 
        llogo=DIR_LEAGUE_IMAGES+row[5]) for row in cursor.fetchall()]
    cursor.close()

    return render_template("team.html", team=team, 
        stadium=stadium, standing=standing, rivaries=rivaries,
        coaches=coaches)


@app.route('/stadium', methods=['GET'])
def stadium():
    sid = request.args.get('id')
    if sid is None:
        abort(400)

    sqlcmd = "SELECT name,country,city,capacity,year_built \
        FROM stadiums WHERE sid={}".format(sid)
    cursor = g.conn.execute(sqlcmd)
    row = cursor.fetchone()
    cursor.close()
    stadium = dict(name=row[0], country=row[1], city=row[2], 
        capacity=row[3], year=row[4])

    # continue to fetch the host team info
    sqlcmd = "SELECT tid,name FROM teams WHERE stadium={}".format(sid)
    cursor = g.conn.execute(sqlcmd)
    teams = [dict(tid=row[0], name=row[1]) for row in cursor.fetchall()]
    cursor.close()

    return render_template("stadium.html", stadium=stadium, teams=teams)


@app.route('/leagues', methods=['GET'])
def leagues():
    # get the enum of countries for 'select'
    cursor = g.conn.execute("SELECT country FROM leagues GROUP BY country ORDER BY country")
    countries = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # parse filters
    filter_country = request.args.get('filter_country')
    sort_by = request.args.get('sort_by')

    sqlcmd = "SELECT lid,name,logo,country,nr_teams,nr_promote,nr_relegate,\
                nr_ecl,year_founded,level \
            FROM leagues"
    
    sqlcmd_where = ""
    if not filter_country is None and not filter_country == 'All':
        sqlcmd_where = add_where_clause(sqlcmd_where, 
            "country='{}'".format(filter_country))

    sqlcmd_order = " ORDER BY country,level"  
    if not sort_by is None:
        if sort_by == '-':
            sqlcmd_order = " ORDER BY country,level"
        elif sort_by == 'Name A-Z':
            sqlcmd_order = " ORDER BY name"
        elif sort_by == 'Name Z-A':
            sqlcmd_order = " ORDER BY name DESC"
        elif sort_by == 'Country':
            sqlcmd_order = " ORDER BY country,level"
        elif sort_by == 'Year founded':
            sqlcmd_order = " ORDER BY year_founded"
        elif sort_by == '# Teams':
            sqlcmd_order = " ORDER BY nr_teams DESC,country,level"
        elif sort_by == '# ECL qualifications':
            sqlcmd_order = " ORDER BY nr_ecl DESC, country"
            sqlcmd_where = add_where_clause(sqlcmd_where, "nr_ecl>0")

    sqlcmd = sqlcmd + sqlcmd_where + sqlcmd_order
    cursor = g.conn.execute(sqlcmd)
    fetchall = cursor.fetchall()
    leagues = [dict(ind=i+1, lid=row[0], name=row[1], 
        logo=DIR_LEAGUE_IMAGES+row[2], country=row[3], nrt=row[4], 
        nrp=str(checked(row[5])).rstrip('0').rstrip('.'), 
        nrr=str(checked(row[6])).rstrip('0').rstrip('.'), 
        nre=str(checked(row[7])).rstrip('0').rstrip('.'), 
        year=checked(row[8]), 
        level=checked(row[9])) for (i, row) in zip(xrange(len(fetchall)), fetchall)]
    cursor.close()
    
    return render_template("leagues.html", leagues=leagues, countries=countries)


@app.route('/league', methods=['GET'])
def league():
    lid = request.args.get('lid')
    if lid is None:
        abort(400)

    sqlcmd = "SELECT l.name,l.logo,l.country,l.nr_teams,l.nr_promote,\
            l.nr_relegate,l.nr_ecl,l.year_founded,l.promote_to,l.relegate_to,\
            l.level,l1.name,l2.name \
        FROM (leagues l LEFT OUTER JOIN leagues l1 ON l.promote_to=l1.lid) \
            LEFT OUTER JOIN leagues l2 ON l.relegate_to=l2.lid \
        WHERE l.lid={}".format(lid)
    cursor = g.conn.execute(sqlcmd)
    row = cursor.fetchone()
    cursor.close()
    league = dict(lid=lid, name=row[0], logo=DIR_LEAGUE_IMAGES+row[1], 
        country=row[2], nrt=row[3],
        nrp=str(checked(row[4])).rstrip('0').rstrip('.'), 
        nrr=str(checked(row[5])).rstrip('0').rstrip('.'), 
        nre=str(checked(row[6])).rstrip('0').rstrip('.'), 
        year=checked(row[7]), prom=checked(row[8]), 
        rele=checked(row[9]), level=checked(row[10]),
        pname=checked(row[11]), rname=checked(row[12]))

    # continue to fetch the seasons
    sqlcmd = "SELECT ss.sid,ss.year_begin,ss.year_end,t.tid,t.name,m.mp \
        FROM seasons ss,teams t, \
            (SELECT season,MIN(position) AS mp FROM standing \
            WHERE league={} GROUP BY season) AS m \
            LEFT OUTER JOIN standing sd ON \
            m.season=sd.season AND m.mp=sd.position \
        WHERE ss.sid=sd.season AND t.tid=sd.team".format(lid)
    cursor = g.conn.execute(sqlcmd)
    rows = cursor.fetchall()
    cursor.close()
    seasons = []
    for row in rows:
        dd = dict(sid=row[0], yr_beg=row[1], yr_end=row[2], 
            tid=None, tname='-')
        if not row[5] is None and row[5] == 1:
            dd['tid'] = row[3]
            dd['tname'] = row[4]
        seasons.append(dd)

    return render_template("league.html", league=league, seasons=seasons)

@app.route('/standing', methods=['GET'])
def standing():
    sid = request.args.get('sid')
    lid = request.args.get('lid')
    tid = chknull(request.args.get('tid'))

    if sid is None or lid is None:
        abort(400)

    # fetch league info
    sqlcmd = "SELECT l.name,l.logo,l.nr_teams,l.nr_promote,l.nr_relegate, \
            l.nr_ecl,l.promote_to,l.relegate_to, \
            l1.name AS pname,l2.name AS rname \
        FROM (leagues l LEFT OUTER JOIN leagues l1 ON l.promote_to=l1.lid) \
            LEFT OUTER JOIN leagues l2 ON l.relegate_to=l2.lid \
        WHERE l.lid={}".format(lid)
    cursor = g.conn.execute(sqlcmd)
    row = cursor.fetchone()
    cursor.close()
    league = dict(lid=lid, lname=row[0], llogo=DIR_LEAGUE_IMAGES+row[1], 
        plid=row[6],rlid=row[7],pname=row[8],rname=row[9])
    # number of teams total, promoted, relegated and qualified for ECL
    [nt, np, nr, ne] = [float(i) if not i is None else None for i in row[2:6]]

    # fetch season info
    sqlcmd = "SELECT year_begin,year_end,date_begin,date_end \
        FROM seasons WHERE sid={}".format(sid)
    cursor = g.conn.execute(sqlcmd)
    row = cursor.fetchone()
    cursor.close()
    season = dict(sid=sid, yr_beg=row[0], yr_end=row[1], 
        date_beg=row[2], date_end=row[3])

    # fetch all standing info
    sqlcmd = "SELECT t.tid,t.name,t.logo,s.match_played,s.match_win, \
            s.match_draw,s.match_loss,s.goal_for,s.goal_against, \
            s.goal_diff,s.points,s.position \
        FROM standing s JOIN teams t ON s.team=t.tid \
        WHERE s.season={} AND s.league={} \
        ORDER BY s.position".format(sid, lid)
    cursor = g.conn.execute(sqlcmd)
    rows = cursor.fetchall()
    cursor.close()
    standing = []
    for row in rows:
        dd = dict(tid=row[0], tname=row[1], tlogo=DIR_TEAM_IMAGES+row[2], 
            pld=row[3], win=row[4], draw=row[5], loss=row[6], 
            gf=row[7], ga=row[8], gd=row[9], 
            pts=row[10], pos=row[11])

        dd['stat'] = ""
        # promote? relegate? ecl?
        # the logic considers number x.5 where .5 means the team must compete
        # with another team in an extra qualification round
        pos = float(dd['pos'])
        if np:
            if pos <= np:
                dd['stat'] = "promote"
            elif pos < np + 1.0:
                dd['stat'] = "promote_qualify"
        if ne:
            if pos <= ne:
                dd['stat'] = "ecl"
            elif pos < ne + 1.0:
                dd['stat'] = "ecl_qualify"
        if nr:
            if pos >= nt - nr + 1.0:
                dd['stat'] = "relegate"
            elif pos > nt - nr:
                dd['stat'] = "relegate_qualify"

        standing.append(dd)

    return render_template("standing.html", standing=standing, 
        league=league, season=season, tid=tid)



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    # g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
    return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
