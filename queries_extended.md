# Soccer Database Project Two

## Modifications to Schema

### (1) Composite Types

The type created is to store addresses:

```sql
CREATE TYPE address AS (
    country         VARCHAR(20),
    state_county    VARCHAR(20),
    city            VARCHAR(20),
    district        VARCHAR(20),
    zipcode         VARCHAR(20),
    street_info     VARCHAR(50),
    latitude        REAL,
    longitude       REAL
);
```
A new column *address* of type address is then added into table *stadiums*. 

<pre lang="sql">
w4111=> \d stadiums
                                   Table "yq2211.stadiums"
   Column   |         Type          |                       Modifiers                        
------------+-----------------------+--------------------------------------------------------
 sid        | integer               | not null default nextval('stadiums_sid_seq'::regclass)
 name       | character varying(40) | not null
 country    | character varying(20) | 
 city       | character varying(20) | 
 capacity   | integer               | 
 year_built | smallint              | 
 <strong>address    | address               | </strong>
Indexes:
    "stadiums_pkey" PRIMARY KEY, btree (sid)
</pre>

The table used to store only the country and city where the stadium locates, now with the new type it contains more detailed information. The original fields of country and city are kept for compatibility with the application. To update the field:

```sql
UPDATE stadiums 
SET address='("England","Greater Manchester","Manchester","Old Trafford",null,"Sir Matt Busby Way",53.463056,-2.291389)' 
WHERE sid=10;
```

### (2) Arrays

A new column *pwin_history* of small integer array type is added to table *coach_works*.

<pre lang="sql">
w4111=> \d coach_works 
              Table "yq2211.coach_works"
    Column    |         Type          |   Modifiers   
--------------+-----------------------+---------------
 cid          | integer               | not null
 tid          | integer               | not null
 year_begin   | smallint              | not null
 year_end     | smallint              | 
 role         | character varying(20) | 
 sacked       | boolean               | default false
 percent_win  | real                  | 
 <strong>pwin_history | smallint[]            | </strong>
Indexes:
    "pk_coach_works" PRIMARY KEY, btree (cid, tid, year_begin)
</pre>

Each element in this array represents the percentage of winning matches within one of the seasons the coach works in the team, ordered from the first season to the last/latest one. Since the number of seasons varies in each case, the length of the array is flexible. The value of *pwin_history* is set via executing:

```sql
UPDATE coach_works 
SET pwin_history='{61,67,36}'
WHERE cid=3 AND tid=4 AND year_begin=2013;
```

### (3) Documents

Two columns *wiki_vector* and *wiki_text* are added to the schema of table *teams*:

<pre lang="sql">
w4111=> \d teams
                                    Table "yq2211.teams"
    Column    |         Type          |                      Modifiers                      
--------------+-----------------------+-----------------------------------------------------
 tid          | integer               | not null default nextval('teams_tid_seq'::regclass)
 name         | character varying(40) | not null
 logo         | character varying(50) | 
 year_founded | smallint              | 
 country      | character varying(20) | not null
 theme_color  | character varying(20) | 
 stadium      | integer               | 
 <strong>wiki_vector  | tsvector              | 
 wiki_text    | text                  | </strong>
Indexes:
    "teams_pkey" PRIMARY KEY, btree (tid)
</pre>

Both columns store the contents of Wikipedia paragraphs of each team, while *wiki_vector* is of type **tsvector** and *wiki_text* is an **unlimited-length string** that stores the original text contents. Both fields are kept so that the table is able to do fast full text search on the tsvector, as well as other operations that requires plain text, e.g. a `ts_headline()` call.

Data is populated by running a [script](https://bitbucket.org/snippets/official_71/8R6zx) with the URL of the Wikipedia web page and the team ID in database.


## SQL Queries

All data populated to database are authentic real-world data the are captured from following resources using scripts or manually:

* [footballdatabase.eu](http://www.footballdatabase.eu)
* [Wikipedia](https://en.wikipedia.org)

### (1) Noisy neighbors

**Objective:** Find pairs of rivalry teams that are closest with each other in distance. Since the *earthdistance* extension is not available, a coarse estimation of distance is applied by calculating the sum of squared difference between the latitude and longitude coordinates of both home stadiums.

```sql
SELECT *
FROM 
	(SELECT t1.name AS team1, t2.name AS team2, r.name AS derby, 
        (((s1.address).latitude - (s2.address).latitude)^2 + ((s1.address).longitude - (s1.address).longitude)^2) AS distance
    FROM rivaries r, teams t1, stadiums s1, teams t2, stadiums s2
    WHERE r.tid1 = t1.tid AND r.tid2 = t2.tid AND 
        t1.stadium = s1.sid AND t2.stadium = s2.sid
    ) AS temp
ORDER BY temp.distance
LIMIT 5;
```

**Explanations:**

* line 3 - calculate distance between all rivalry teams.
* line 1 - list the 5 rivalries with smallest distances between them.

**Results:**

```
      team1       |       team2       |        derby         |       distance       
------------------+-------------------+----------------------+----------------------
 Everton          | Liverpool         | 'Merseyside derby'   | 6.49709400022402e-05
 Manchester City  | Manchester United | 'Manchester derby'   | 0.000400018310756423
 Liverpool        | Manchester United | 'Northwest derby'    |  0.00103855133056641
 Arsenal          | Tottenham Hotspur | 'North London derby' |  0.00233600294450298
 Newcastle United | Sunderland        | 'Tyne-Wear derby'    |  0.00374020636081696
(5 rows)

```

### (2) 'So much for the happy ending'

**Objective:** Find the managers that managed a team for over one season, had a good opening season but ended in a much less successful one.

```sql
SELECT (p.first_name||' '||p.last_name) AS name, t.name AS team, 
	temp.year_begin, temp.percent_begin, 
	temp.year_end, temp.percent_end
FROM coaches c, people p, teams t, 
	(SELECT cid, tid, year_begin, year_end, 
		pwin_history[1] AS percent_begin, 
		pwin_history[array_length(pwin_history, 1)] AS percent_end
    FROM coach_works
    WHERE role = 'manager' AND
    	array_length(pwin_history, 1) > 1 AND 
    	pwin_history[1] >= 60 AND 
    	pwin_history[array_length(pwin_history, 1)] <= pwin_history[1] - 10
    ) AS temp
WHERE c.cid = temp.cid AND c.pid = p.pid AND t.tid = temp.tid;

```

**Explanations:**

* line 5 - find the coach-works-in-team relations that matches the following criteria: *1)* the role is manager, *2)* for at least 2 seasons, *3)* with the win% in the first season more than 60% and *4)* the win% of the last season 10%(absolute) lower or worse compared with the first season.
* line 1 - join with other tables for more information.

**Results:**

```
      name       |       team       | year_begin | percent_begin | year_end | percent_end 
-----------------+------------------+------------+---------------+----------+-------------
 José Mourinho   | Chelsea          |       2004 |            71 |     2007 |          38
 José Mourinho   | Real Madrid C.F. |       2010 |            75 |     2013 |          62
 José Mourinho   | Chelsea          |       2013 |            61 |     2015 |          36
 Carlo Ancelotti | Chelsea          |       2009 |            70 |     2011 |          53
(4 rows)

```


### (3) The Big Four

**Objective:** Find the *Big Four* in England, which is the four teams most related to terms such as *win*, *champion* and *trophy*.


```sql
SELECT name,rank,
	ts_headline('english',wiki_text,to_tsquery(
	    'win & champion & trophies'),
	    'StartSel=<, StopSel=>, MaxWords=6, MinWords=2, MaxFragments=10, FragmentDelimiter=...') 
FROM 
	(SELECT name,wiki_text,ts_rank_cd(wiki_vector, q) AS rank 
    FROM teams, to_tsquery(
        'win & champion & trophies') q 
    WHERE wiki_vector @@ q AND country='England'
    ORDER BY rank DESC 
    LIMIT 4) AS foo;
```

**Explanations:**

* line 6 - find the 4 teams of which the Wikipedia contents **tsvector** has the highest ranks matching keywords *win, champion, tropies*, and sort them by the rank.
* line 1 - list the teams and highlight the pieces of Wikipedia contents **text** that match those keywords.

**Results:**

```
       name        |   rank    |                                                                                                                                                                                    ts_headline                                                                                                                                                                                     
-------------------+-----------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Chelsea           | 0.0361883 | reigning <champions>. Founded...decades; <winning> 21 <trophies> since...UEFA <Champions> League, two UEFA...<win> the UEFA <Champions> League...first major <trophy> success  the League...European <Champions> Cup, but after objections...season, <winning> the League...immediately by <winning> the Second Division...<win> the <trophy>...<win> all four European <trophies>
 Arsenal           | 0.0168916 | first national <trophy>...returned to <win>...equalled the <champions> of England record...<win> the League...<Champions> squad...competitive European <trophy>, the 196970 Inter...<champions> of England record.[43] This...Double-<winning> side was soon broken...clubs only <trophy> during this time...<win> in the game, <winning> their
 Manchester United | 0.0166946 | UEFA <Champions> League...also, by <winning> the UEFA Europa...<winning> all three top domestic <trophies>...club to <win> the European...<trophies> as manager, including 13 Premier...UEFA <Champions> Leagues, between...back title <winning> side...team to <win> the Premier League...UEFA <Champions> League  The Treble...UEFA <Champions> League Final, Teddy Sheringham
 Manchester City   | 0.0146091 | <win> a European <trophy>...domestic <trophy> in the same season...league <champions> on two occasions...needed to <win> to have...<win> at Old Trafford and confirm...final <trophy> of the clubs most...ever European <trophy> winners...derby <win>.[24] City also qualified...<Champions> League, and competed...major <trophy> since <winning>
(4 rows)


```
