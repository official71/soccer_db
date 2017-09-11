 tid |         name         | sid |            name            
-----+----------------------+-----+----------------------------
   1 | AFC Bournemouth      |   1 | Dean Court
   2 | Arsenal              |   2 | Emirates Stadium
   3 | Aston Villa          |   3 | Villa Park
   4 | Chelsea              |   4 | Stamford Bridge
   5 | Crystal Palace       |   5 | Selhurst Park
   6 | Everton              |   6 | Goodison Park
   7 | Leicester City       |   7 | King Power Stadium
   8 | Liverpool            |   8 | Anfield
   9 | Manchester City      |   9 | City of Manchester Stadium
  10 | Manchester United    |  10 | Old Trafford
  11 | Newcastle United     |  11 | St James' Park
  12 | Norwich City         |  12 | Carrow Road
  13 | Southampton          |  13 | St. Mary's Stadium
  14 | Stoke City           |  14 | bet365 Stadium
  15 | Sunderland           |  15 | Stadium of Light
  16 | Swansea City         |  16 | Liberty Stadium
  17 | Tottenham Hotspur    |  17 | White Hart Lane
  18 | Watford              |  18 | Vicarage Road Stadium
  19 | West Bromwich Albion |  19 | The Hawthorns
  20 | West Ham United      |  21 | London Stadium
  31 | Juventus F.C.        |  23 | Allianz Stadium
(21 rows)


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

UPDATE stadiums 
SET address='("England","North East England","Newcastle",null,null,null,54.975556,-1.621667)' 
WHERE sid=11;

UPDATE stadiums 
SET address='("England","North East England","Sunderland",null,null,null,54.9144,-1.3882)' 
WHERE sid=15;

UPDATE stadiums 
SET address='("England",null,"London","Highbury","N7",null,51.555,-0.108611)' 
WHERE sid=2;

UPDATE stadiums 
SET address='("England",null,"London","Fulham","SW6",null,51.481667,-0.191111)' 
WHERE sid=4;

UPDATE stadiums 
SET address='("England",null,"London","South Norwood","SE25",null,51.398333,-0.085556)' 
WHERE sid=5;

UPDATE stadiums 
SET address='("England","Merseyside","Liverpool","Walton",null,"Goodison Road",53.438889,-2.966389)' 
WHERE sid=6;

UPDATE stadiums 
SET address='("England","Merseyside","Liverpool","Anfield",null,null,53.430828,-2.960847)' 
WHERE sid=8;

UPDATE stadiums 
SET address='("England","Greater Manchester","Manchester","Etihad Campus","M11 3FF",null,53.483056,-2.200278)' 
WHERE sid=9;

UPDATE stadiums 
SET address='("England","Greater Manchester","Manchester","Old Trafford",null,"Sir Matt Busby Way",53.463056,-2.291389)' 
WHERE sid=10;

UPDATE stadiums 
SET address='("England",null,"London","Tottenham","N17",null,51.603333,-0.065833)' 
WHERE sid=17;

UPDATE stadiums 
SET address='("England",null,"London",null,"E20","Marshgate Lane",51.538611,-0.016389)' 
WHERE sid=21;

UPDATE stadiums 
SET address='("England","Hampshire","Southampton",null,"SO17","Britannia Rd",50.905833,-1.391111)' 
WHERE sid=13;


SELECT *
FROM 
    (SELECT t1.name AS team1, t2.name AS team2, r.name AS derby, 
        (((s1.address).latitude - (s2.address).latitude)^2 + ((s1.address).longitude - (s1.address).longitude)^2) AS distance
    FROM rivaries r, teams t1, stadiums s1, teams t2, stadiums s2
    WHERE r.tid1 = t1.tid AND r.tid2 = t2.tid AND 
        t1.stadium = s1.sid AND t2.stadium = s2.sid
    ) AS temp
ORDER BY temp.distance
LIMIT 5
;



