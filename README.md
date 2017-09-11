#Soccer Database Project

##URL of Web Application

[http://104.196.148.***:8111/](obsolete)

##Description of Implementation

The application is built upon the PostgreSQL soccer database. It allows end-users to query data regarding multiple European soccer leagues, teams(clubs), season standings(results), stadiums and people from the database, as well as insertion and deletion operations. The queries are not straightforward, they require nested operations from different tables and answer questions such as "who ever worked for Arsenal as a manager and what was the winning rate?" or "list all previous seasons and their champions (teams whose position equals to 1) of the Premier League".

##Web Pages of Interest

###(1) Teams

**URL:** [http://104.196.148.***:8111/teams](obsolete)

**Description:** This page lists all the teams that are stored in table `teams`. It provides several functions using SQL queries:

* **Team information** shows brief information of each team upon `GET` request to URL `/teams`. The primary key of the table is not shown explicitly, but it forms a hyperlink together with the team name so that users can visit the detailed page of the specified team.
* **Filtering** teams by country is supported by providing a `select` input and including the value of `select` as a parameter into the `GET` request, then a `WHERE country='xxx'` clause is appended to the original query statement. The options of `select` are acquired via querying table `teams` with `GROUP BY` clause.
* **Ordering** teams either by country, year founded or alphabetically is supported by providing a form with another `select` input, which will cause a `ORDER BY` clause in the SQL query.
* **Adding** a new team into database is implemented by providing a form that `POST` to the URL. The information of the new team is gathered via `text` inputs (e.g. team name) or `select` inputs (e.g. select a stadium in database). An `INSERT INTO teams ...` query is made when the form is submitted.
* **Deleting** an existing team from database is implemented likewise. The input is only a `select` from all teams in database. The deletion form `POST` to another URL but redirects to `/teams` URL after executing the `DELETE FROM teams ...` query to show the results.


###(2) Season Standing

**URL:** [http://104.196.148.***:8111/standing?sid=2&lid=1](obsolete)

**Description:** This page gives the standing of teams in the specified season and league. Most data needed for this page is in table `standing`, however it also requires data joint from other tables such as `teams`, `seasons` and `leagues`.

* **Season and league** keys are retrieved using request arguments `sid` and `lid`, which are primary keys of table `seasons` and `leagues`. Information such as season staring date and league logo image are then fetched from the database using these keys.
* **Teams** that participated in the season under the league are listed using `WHERE` clause and `ORDER BY` their positions, with `position=1` being the champion. The query `INNER JOIN` table `standing` and `teams` on team ID to obtain team information.
* **Qualificaton or relegation** information of a certain team is not stored explicitly in database, thus it involves two data sets: the number of teams to promote/relegate in the league and the team's position in the league. The application computes the result after querying both data.
* **The league to promote or relegate to** is obtained by applying `OUTER JOIN` to `leagues` tables on league ID. The data for the dedicated league forms a hyperlink to the page of that league.