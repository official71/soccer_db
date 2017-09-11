 cid | last_name | tid |       name        | year_begin | year_end 
-----+-----------+-----+-------------------+------------+----------
   5 | Zidane    |  21 | Real Madrid C.F.  |       2016 |         
   6 | Guardiola |  22 | FC Barcelona      |       2008 |     2012
   6 | Guardiola |   9 | Manchester City   |       2016 |         
   4 | Conte     |   4 | Chelsea           |       2016 |         
   3 | Mourinho  |   4 | Chelsea           |       2004 |     2007
   3 | Mourinho  |  21 | Real Madrid C.F.  |       2010 |     2013
   3 | Mourinho  |   4 | Chelsea           |       2013 |     2015
   3 | Mourinho  |  10 | Manchester United |       2016 |         
   2 | Bould     |   2 | Arsenal           |       2012 |         
   1 | Wenger    |   2 | Arsenal           |       1996 |         
(10 rows)


UPDATE coach_works SET pwin_history='{44,57,57,56,54,65,58,63,61,54,51,62,54,60,53,57,55,63,63,52,64}'
WHERE cid=1 AND tid=2;

UPDATE coach_works SET pwin_history='{78}'
WHERE cid=5 AND tid=21;

UPDATE coach_works SET pwin_history='{68,76,73,73}'
WHERE cid=6 AND tid=22;

UPDATE coach_works SET pwin_history='{59}'
WHERE cid=6 AND tid=9;

UPDATE coach_works SET pwin_history='{79}'
WHERE cid=4 AND tid=4;

UPDATE coach_works SET pwin_history='{71,69,66,38}'
WHERE cid=3 AND tid=4 AND year_begin=2004;

UPDATE coach_works SET pwin_history='{75,79,62}'
WHERE cid=3 AND tid=21;

UPDATE coach_works SET pwin_history='{61,67,36}'
WHERE cid=3 AND tid=4 AND year_begin=2013;

UPDATE coach_works SET pwin_history='{58}'
WHERE cid=3 AND tid=10;



SELECT p.first_name || ' ' || p.last_name AS name,t.name AS team,temp.year_begin,
    temp.percent_begin,temp.year_end,temp.percent_end
FROM coaches c, people p, teams t,
    (SELECT cid,tid,year_begin,year_end,pwin_history[1] AS percent_begin,pwin_history[array_length(pwin_history, 1)] AS percent_end
    FROM coach_works
    WHERE array_length(pwin_history, 1) > 1 AND
        pwin_history[1] >= 60 AND
        pwin_history[array_length(pwin_history, 1)] <= pwin_history[1] - 10) AS temp
WHERE c.cid=temp.cid AND c.pid=p.pid AND t.tid=temp.tid;
