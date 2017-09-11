CREATE TABLE leagues (
    lid             serial PRIMARY KEY,
    name            varchar(40) NOT NULL,
    logo            varchar(50),
    country         varchar(20),
    nr_teams        smallint NOT NULL,
    nr_promote      real DEFAULT 0,
    nr_relegate     real DEFAULT 0,
    nr_ecl          real DEFAULT 0,
    year_founded    smallint,
    promote_to      integer,
    relegate_to     integer,
    CONSTRAINT fk_promote FOREIGN KEY (promote_to) REFERENCES leagues (lid) ON DELETE SET NULL,
    CONSTRAINT fk_relegate FOREIGN KEY (relegate_to) REFERENCES leagues (lid) ON DELETE SET NULL,
    CONSTRAINT uniq1 UNIQUE(name, country)
);

CREATE TABLE seasons (
    sid             serial PRIMARY KEY,
    year_begin      smallint NOT NULL,
    year_end        smallint NOT NULL,
    date_begin      date NOT NULL,
    date_end        date NOT NULL,
    description     varchar(20),
    CONSTRAINT uniq_season UNIQUE(year_begin, year_end, date_begin, date_end)
);

CREATE TABLE stadiums (
    sid             serial PRIMARY KEY,
    name            varchar(40) NOT NULL,
    country         varchar(20),
    city            varchar(20),
    capacity        integer,
    year_built      smallint
);

CREATE TABLE teams (
    tid             serial PRIMARY KEY,
    name            varchar(40) NOT NULL,
    logo            varchar(50),
    year_founded    smallint,
    country         varchar(20) NOT NULL,
    theme_color     varchar(20),
    stadium         integer,
    CONSTRAINT uniq_team UNIQUE(name, country),
    CONSTRAINT fk_team_stadium FOREIGN KEY (stadium) REFERENCES stadiums (sid) ON DELETE SET NULL
);

CREATE TABLE standing (
    team            integer NOT NULL,
    season          integer NOT NULL,
    league          integer NOT NULL,
    match_played    smallint DEFAULT 0,
    match_win       smallint DEFAULT 0,
    match_draw      smallint DEFAULT 0,
    match_loss      smallint DEFAULT 0,
    goal_for        smallint DEFAULT 0,
    goal_against    smallint DEFAULT 0,
    goal_diff       smallint DEFAULT 0,
    points          smallint DEFAULT 0,
    position        smallint DEFAULT 0,
    CONSTRAINT pk_standing PRIMARY KEY (team, season, league),
    CONSTRAINT fk_standing_team FOREIGN KEY (team) REFERENCES teams (tid) ON DELETE NO ACTION,
    CONSTRAINT fk_standing_season FOREIGN KEY (season) REFERENCES seasons (sid) ON DELETE NO ACTION,
    CONSTRAINT fk_standing_league FOREIGN KEY (league) REFERENCES leagues (lid) ON DELETE NO ACTION,
    CONSTRAINT uniq_standing2 UNIQUE(position, season, league)
);

CREATE TABLE people (
    pid             serial PRIMARY KEY,
    first_name      varchar(20),
    middle_name     varchar(20),
    last_name       varchar(20) NOT NULL,
    nationality     varchar(20),
    dob             date,
    height          smallint,
    weight          smallint
);

CREATE TABLE coaches (
    cid             serial PRIMARY KEY,
    pid             integer NOT NULL,
    career_begin    smallint,
    team_begin      integer,
    career_end      smallint,
    team_end        integer,
    rating          smallint,
    tactics         smallint,
    CONSTRAINT fk_coach_pid FOREIGN KEY (pid) REFERENCES people (pid) ON DELETE CASCADE,
    CONSTRAINT fk_coach_team1 FOREIGN KEY (team_begin) REFERENCES teams (tid) ON DELETE SET NULL,
    CONSTRAINT fk_coach_team2 FOREIGN KEY (team_end) REFERENCES teams (tid) ON DELETE SET NULL
);

CREATE TABLE players (
    pid             serial PRIMARY KEY,
    person_id       integer NOT NULL,
    position        varchar(10),
    nr_goals        smallint DEFAULT 0,
    team_begin      integer,
    career_end      smallint,
    team_end        integer,
    rating          smallint,
    attacking       smallint,
    defending       smallint,
    goalkeeping     smallint,
    career_begin    smallint,
    CONSTRAINT fk_player_pid FOREIGN KEY (person_id) REFERENCES people (pid) ON DELETE CASCADE,
    CONSTRAINT fk_player_team1 FOREIGN KEY (team_begin) REFERENCES teams (tid) ON DELETE SET NULL,
    CONSTRAINT fk_player_team2 FOREIGN KEY (team_end) REFERENCES teams (tid) ON DELETE SET NULL
);

CREATE TABLE matches (
    mid             serial PRIMARY KEY,
    match_date      date NOT NULL,
    kickoff_time    time,
    extra_minutes   smallint DEFAULT 0,
    stadium         integer,
    attendance      integer,
    referee         integer,
    home_team       integer NOT NULL,
    away_team       integer NOT NULL,
    home_score      integer DEFAULT 0,
    away_score      integer DEFAULT 0,
    home_score_pen  integer DEFAULT 0,
    away_score_pen  integer DEFAULT 0,
    home_booking    integer DEFAULT 0,
    away_booking    integer DEFAULT 0,
    CONSTRAINT fk_match_stadium FOREIGN KEY (stadium) REFERENCES stadiums (sid) ON DELETE SET NULL,
    CONSTRAINT fk_match_referee FOREIGN KEY (referee) REFERENCES people (pid) ON DELETE SET NULL,
    CONSTRAINT fk_match_team1 FOREIGN KEY (home_team) REFERENCES teams (tid) ON DELETE NO ACTION,
    CONSTRAINT fk_match_team2 FOREIGN KEY (away_team) REFERENCES teams (tid) ON DELETE NO ACTION
);

CREATE TABLE player_works (
    pid             integer NOT NULL,
    team            integer NOT NULL,
    season          integer NOT NULL,
    league          integer NOT NULL,
    number          smallint,
    wage            integer,
    position        varchar(10),
    appearances     smallint DEFAULT 0,
    goals           smallint DEFAULT 0,
    assists         smallint DEFAULT 0,
    avg_rating      real DEFAULT 0,
    CONSTRAINT pk_player_works PRIMARY KEY (pid, team, season, league),
    CONSTRAINT fk_player_works_pid FOREIGN KEY (pid) REFERENCES players (pid) ON DELETE CASCADE,
    CONSTRAINT fk_player_works_sid FOREIGN KEY (team, season, league) REFERENCES standing ON DELETE CASCADE
);

CREATE TABLE coach_works (
    cid             integer NOT NULL,
    tid             integer NOT NULL,
    year_begin      smallint NOT NULL,
    year_end        smallint,
    role            varchar(20),
    sacked          boolean DEFAULT FALSE,
    CONSTRAINT pk_coach_works PRIMARY KEY (cid, tid, year_begin),
    CONSTRAINT fk_coach_works_cid FOREIGN KEY (cid) REFERENCES coaches (cid) ON DELETE CASCADE,
    CONSTRAINT fk_coach_works_tid FOREIGN KEY (tid) REFERENCES teams (tid) ON DELETE CASCADE
);

CREATE TABLE player_plays (
    pid             integer NOT NULL,
    mid             integer NOT NULL,
    home_side       boolean NOT NULL,
    minute_on       smallint DEFAULT 0,
    minute_off      smallint DEFAULT -1,
    CONSTRAINT pk_player_plays PRIMARY KEY (pid, mid),
    CONSTRAINT fk_player_plays_pid FOREIGN KEY (pid) REFERENCES players (pid) ON DELETE CASCADE,
    CONSTRAINT fk_player_plays_mid FOREIGN KEY (mid) REFERENCES matches (mid) ON DELETE CASCADE
);

CREATE TABLE player_scores (
    pid             integer NOT NULL,
    mid             integer NOT NULL,
    self_score      smallint NOT NULL,
    opp_score       smallint NOT NULL,
    minute          smallint NOT NULL,
    in_extra_time   boolean DEFAULT FALSE NOT NULL,
    pid_assist      integer,
    is_penalty      boolean DEFAULT FALSE,
    is_owngoal      boolean DEFAULT FALSE,
    CONSTRAINT pk_player_scores PRIMARY KEY (pid, mid, self_score, opp_score),
    CONSTRAINT fk_player_scores_pid FOREIGN KEY (pid) REFERENCES players (pid) ON DELETE CASCADE,
    CONSTRAINT fk_player_scores_mid FOREIGN KEY (mid) REFERENCES matches (mid) ON DELETE CASCADE,
    CONSTRAINT fk_player_scores_plays FOREIGN KEY (pid,mid) REFERENCES player_plays ON DELETE CASCADE,
    CONSTRAINT fk_player_scores_pid_assist FOREIGN KEY (pid_assist) REFERENCES players (pid) ON DELETE SET NULL
);

CREATE TABLE rivaries (
    tid1            integer,
    tid2            integer,
    name            varchar(50),
    CONSTRAINT pk_rivaries PRIMARY KEY (tid1, tid2),
    CONSTRAINT fk_rivaries_tid1 FOREIGN KEY (tid1) REFERENCES teams (tid) ON DELETE CASCADE,
    CONSTRAINT fk_rivaries_tid2 FOREIGN KEY (tid2) REFERENCES teams (tid) ON DELETE CASCADE
);