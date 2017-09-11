#Soccer Database

##Schema

###1. Person

```SQL
`person_id`		INT
`first_name`	CHAR
`middle_name`	CHAR
`last_name`		CHAR, NOT NULL #or name on shirt
`nationality`	CHAR
`dob`			DATE
`height`		INT #in centimeters
`weight`		INT #in kilograms

PRIMARY KEY		`person_id`
```

###2. Coach

```SQL
`coach_id`		INT
`person_id`		INT, NOT NULL
`career_begin`	INT #year when career as a coach begins
`team_begin`	INT
`career_end`	INT #year when career as a coach ends
`team_end`		INT
`rating`		INT #0-20 rating of overall capability
...				INT #ratings of specific capabilities (e.g. tactics)

PRIMARY KEY		`coach_id`
FOREIGN KEY		`person_id` REFERENCES `Person`(`person_id`) ON DELETE CASCADE
FOREIGN KEY		`team_begin` REFERENCES `Team`(`team_id`) ON DELETE SET NULL
FOREIGN KEY		`team_end` REFERENCES `Team`(`team_id`) ON DELETE SET NULL
```

###3. Player

```SQL
`player_id`		INT
`person_id`		INT, NOT NULL
`position`		CHAR #'D'efensive, 'F'orward, 'M'idfielder, 'G'oalie
`nr_goals`		INT, DEFAULT 0 #overall goals
`career_begin`	INT #year when career as a player begins
`team_begin`	INT
`career_end`	INT #year when career as a player ends
`team_end`		INT
`rating`		INT #0-100 rating of player's overall capability
...				INT #ratings of specific capabilities (e.g. shooting)

PRIMARY KEY		`coach_id`
FOREIGN KEY		`person_id` REFERENCES `Person`(`person_id`) ON DELETE CASCADE
FOREIGN KEY		`team_begin` REFERENCES `Team`(`team_id`) ON DELETE SET NULL
FOREIGN KEY		`team_end` REFERENCES `Team`(`team_id`) ON DELETE SET NULL
```

###4. Arena

```SQL
`arena_id`		INT
`arena_name`	CHAR, NOT NULL
`country`		CHAR
`city`			CHAR
`capacity`		INT
`year_built`	INT

PRIMARY KEY		`arena_id`
```

###5. Team

```SQL
`team_id`		INT
`team_name`		CHAR, NOT NULL
`team_logo`		CHAR #link to image
`year_begin`	INT #year founded in
`country`		CHAR, NOT NULL
`color`			CHAR #theme color of home kits
`arena_id`		INT, NOT NULL

PRIMARY KEY		`team_id`
UNIQUE			`team_name`
FOREIGN KEY		`arena_id` REFERENCES `Arena`(`arena_id`) ON DELETE NO ACTION
```

###6. Season

```SQL
`season_id`		INT
`year_begin`	INT, NOT NULL
`year_end`		INT, NOT NULL
`date_begin`	DATE, NOT NULL #MM/DD/YYYY
`date_end`		DATE, NOT NULL #MM/DD/YYYY

PRIMARY KEY		`season_id`
UNIQUE			(`year_begin`, `year_end`, `date_begin`, `date_end`)
```

###7. League

```SQL
`league_id`		INT
`league_name`	CHAR, NOT NULL
`league_logo`	CHAR #link to image
`country`		CHAR, NOT NULL
`nr_teams`		INT, NOT NULL #number of teams
`nr_promote`	INT, DEFAULT 0 #number of teams to promote
`nr_relegate`	INT, DEFAULT 0 #number of teams to relegate
`nr_ecl`		INT, DEFAULT 0 #number of teams to qualify for ECL
`year_begin`	INT, NOT NULL #league history

PRIMARY KEY		`league_id`
```

###8. Standing

```SQL
`standing_id`	INT
`team_id`		INT	
`season_id`		INT
`league_id`		INT
`match_played`	INT, DEFAULT 0
`match_win`		INT, DEFAULT 0
`match_loss`	INT, DEFAULT 0
`match_draw`	INT, DEFAULT 0
`goal_for`		INT, DEFAULT 0
`goal_against`	INT, DEFAULT 0
`goal_diff`		INT, DEFAULT 0
`points`		INT, DEFAULT 0
`position`		INT, DEFAULT 0

PRIMARY KEY 	`standing_id`
FOREIGN KEY		`team_id` REFERENCES `Team`(`team_id`) ON DELETE NO ACTION
FOREIGN KEY		`season_id` REFERENCES `Season`(`season_id`) ON DELETE NO ACTION
FOREIGN KEY		`league_id` REFERENCES `League`(`league_id`) ON DELETE NO ACTION
UNIQUE			(`team_id`, `season_id`, `league_id`)
```

###9. Match

```SQL
`match_id`		INT
`date`			DATE, NOT NULL #kickoff date MM/DD/YYYY
`time`			TIME, NOT NULL #kickoff time
`extra_time`	INT, DEFAULT 0 #extra time minutes
`arena`			INT
`attendance`	INT
`referee`		INT
`home_team`		INT, NOT NULL
`away_team`		INT, NOT NULL
`home_score`	INT, DEFAULT 0 #score in regular match time
`away_score`	INT, DEFAULT 0
`home_score_pen`	INT, DEFAULT 0 #score in penalty shootout
`away_score_pen`	INT, DEFAULT 0
`home_booking`	INT, DEFAULT 0 #booking includes yellow/red cards
`away_booking`	INT, DEFAULT 0

PRIMARY KEY		`match_id`
UNIQUE			(`date`, `home_team`, `away_team`)
FOREIGN KEY		`arena` REFERENCES `Arena`(`arena_id`) ON DELETE SET NULL
FOREIGN KEY		`referee` REFERENCES `Person`(`person_id`) ON DELETE SET NULL
FOREIGN KEY		`home_team` REFERENCES `Standing`(`standing_id`)
FOREIGN KEY		`away_team` REFERENCES `Standing`(`standing_id`)
```

\* The field `season_id` of the two instances referred by `home_team` and `away_team` must be identical. Same is the field `league_id`.

###10. Player-Works

```SQL
`player_id`		INT
`standing_id`	INT
`number`		INT, NOT NULL #kit number
`halfway_in`	BOOLEAN, DEFAULT FALSE #joined after season starts
`rent_from`		INT
`wage`			INT #weekly payment in local currency
`position`		CHAR #'D'efensive, 'F'orward, 'M'idfielder, 'G'oalie
`nr_app`		INT, DEFAULT 0 #number of appearances
`nr_goals`		INT, DEFAULT 0
`nr_assists`	INT, DEFAULT 0
`average_rating`	REAL, DEFAULT 0.0 #average match rating 0-10

PRIMARY KEY		(`player_id`, `standing_id`)
FOREIGN KEY		`player_id` REFERENCES `Player`(`player_id`) ON DELETE CASCADE
FOREIGN KEY		`standing_id` REFERENCES `Standing`(`standing_id`) ON DELETE CASCADE
FOREIGN KEY		`rent_from` REFERENCES `Team`(`team_id`) ON DELETE SET NULL
```

###11. Coach-Works

```SQL
`coach_id`		INT
`team_id`		INT
`year_begin`	INT
`year_end`		INT
`role`			CHAR #'Manager', 'Attacking', 'Defensive', etc.
`sacked`		BOOLEAN, DEFAULT FALSE #whether sacked from team

PRIMARY KEY		(`coach_id`, `team_id`, `year_begin`, `year_end`)
FOREIGN KEY		`coach_id` REFERENCES `Coach`(`coach_id`) ON DELETE CASCADE
FOREIGN KEY		`team_id` REFERENCES `Team`(`team_id`) ON DELETE CASCADE
```

###12. Player-Plays

```SQL
`player_id`		INT
`match_id`		INT
`home_side`		BOOLEAN, NOT NULL #whether plays for home team
`minute_begin`	INT, DEFAULT 0
`minute_end`	INT, DEFAULT -1 #default means the end of match

PRIMARY KEY		(`player_id`, `match_id`)
FOREIGN KEY		`player_id` REFERENCES `Player`(`player_id`) ON DELETE CASCADE
FOREIGN KEY		`match_id` REFERENCES `Match`(`match_id`) ON DELETE CASCADE
```

###13. Player-Scores

```SQL
`player_id`		INT
`match_id`		INT
`self_score`	INT #scores of self team after scoring
`opp_score`		INT #scores of opponent team after scoring
`minute`		INT, NOT NULL
`extra_time`	BOOLEAN #if the score is in extra time
`penalty`		BOOLEAN, DEFAULT FALSE
`own_goal`		BOOLEAN, DEFAULT FALSE
`player_assist`	INT

PRIMARY KEY		(`player_id`, `match_id`, `self_score`, `opp_score`)
FOREIGN KEY		`player_id` REFERENCES `Player`(`player_id`) ON DELETE CASCADE
FOREIGN KEY		`match_id` REFERENCES `Match`(`match_id`) ON DELETE CASCADE
FOREIGN KEY		`player_assist` REFERENCES `Player`(`player_id`) ON DELETE SET NULL
```


