 tid |         name         
-----+----------------------
   1 | AFC Bournemouth
   2 | Arsenal
   3 | Aston Villa
   4 | Chelsea
   5 | Crystal Palace
   6 | Everton
   7 | Leicester City
   8 | Liverpool
   9 | Manchester City
  10 | Manchester United
  11 | Newcastle United
  12 | Norwich City
  13 | Southampton
  14 | Stoke City
  15 | Sunderland
  16 | Swansea City
  17 | Tottenham Hotspur
  18 | Watford
  19 | West Bromwich Albion
  20 | West Ham United
  21 | Real Madrid C.F.
  22 | FC Barcelona
  31 | Juventus F.C.
(23 rows)

python wiki.py https://en.wikipedia.org/wiki/Leicester_City_F.C. 7
python wiki.py https://en.wikipedia.org/wiki/Arsenal_F.C. 2
python wiki.py https://en.wikipedia.org/wiki/Tottenham_Hotspur_F.C. 17
python wiki.py https://en.wikipedia.org/wiki/Manchester_City_F.C. 9
python wiki.py https://en.wikipedia.org/wiki/Manchester_United_F.C. 10
python wiki.py https://en.wikipedia.org/wiki/Southampton_F.C. 13
python wiki.py https://en.wikipedia.org/wiki/West_Ham_United_F.C. 20
python wiki.py https://en.wikipedia.org/wiki/Liverpool_F.C. 8
python wiki.py https://en.wikipedia.org/wiki/Stoke_City_F.C. 14
python wiki.py https://en.wikipedia.org/wiki/Chelsea_F.C. 4
python wiki.py https://en.wikipedia.org/wiki/Everton_F.C. 6
python wiki.py https://en.wikipedia.org/wiki/Swansea_City_A.F.C. 16
python wiki.py https://en.wikipedia.org/wiki/Watford_F.C. 18
python wiki.py https://en.wikipedia.org/wiki/West_Bromwich_Albion_F.C. 19
python wiki.py https://en.wikipedia.org/wiki/Crystal_Palace_F.C. 5
python wiki.py https://en.wikipedia.org/wiki/A.F.C._Bournemouth 1
python wiki.py https://en.wikipedia.org/wiki/Sunderland_A.F.C. 15
python wiki.py https://en.wikipedia.org/wiki/Newcastle_United_F.C. 11
python wiki.py https://en.wikipedia.org/wiki/Norwich_City_F.C. 12
python wiki.py https://en.wikipedia.org/wiki/Aston_Villa_F.C. 3
python wiki.py https://en.wikipedia.org/wiki/Real_Madrid_C.F. 21
python wiki.py https://en.wikipedia.org/wiki/FC_Barcelona 22
python wiki.py https://en.wikipedia.org/wiki/Juventus_F.C. 31





SELECT name,rank,
        ts_headline('english',wiki_text,to_tsquery(
            'win & champion & trophies'),
            'StartSel=<, StopSel=>, MaxWords=6, MinWords=2, MaxFragments=10, FragmentDelimiter= ... ') 
FROM (SELECT name,wiki_text,ts_rank_cd(wiki_vector, q) AS rank 
        FROM teams, to_tsquery(
            'win & champion & trophies') q 
        WHERE wiki_vector @@ q AND country='England'
        ORDER BY rank DESC 
        LIMIT 4) AS foo;




