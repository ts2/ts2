DROP TABLE IF EXISTS trackitems;
CREATE TABLE trackitems (
        tiid INTEGER PRIMARY KEY,
        name VARCHAR(25) UNIQUE,
        titype VARCHAR(5),
        ptiid INTEGER,
        ntiid INTEGER,
        rtiid INTEGER,
        conflicttiid INTEGER,
        x DOUBLE,
        y DOUBLE,
        xf DOUBLE,
        yf DOUBLE,
        xr DOUBLE,
        yr DOUBLE,
        xn DOUBLE,
        yn DOUBLE,
        reverse BOOLEAN,
        reallength DOUBLE,
        maxspeed DOUBLE,
        placecode VARCHAR(10),
        trackcode VARCHAR(10),
        timersw DOUBLE,
        timerwc DOUBLE);
        
DROP TABLE IF EXISTS places;
CREATE TABLE places (
		placecode VARCHAR(10),
		placename VARCHAR(50),
		x DOUBLE,
		y DOUBLE);
        
DROP TABLE IF EXISTS routes;
CREATE TABLE routes (
        routenum INTEGER PRIMARY KEY,
        beginsignal INTEGER,
        endsignal INTEGER);

DROP TABLE IF EXISTS directions;
CREATE TABLE directions (
        routenum INTEGER,
        tiid INTEGER,
        direction INTEGER);
  
DROP TABLE IF EXISTS routeconflicts;
CREATE TABLE routeconflicts (
        routenum1 INTEGER,
        routenum2 INTEGER);
        
DROP TABLE IF EXISTS traintypes;
CREATE TABLE traintypes (
        code VARCHAR(10),
        description VARCHAR(200),
        maxspeed DOUBLE,
        stdaccel DOUBLE,
        stdbraking DOUBLE,
        emergbraking DOUBLE,
        tlength DOUBLE);
        
DROP TABLE IF EXISTS trains;
CREATE TABLE trains (
        servicecode VARCHAR(10),
        traintype VARCHAR(10),
        speed DOUBLE,
        accel DOUBLE,
        tiid INTEGER,
        previoustiid INTEGER,
        posonti DOUBLE,
        appeartime TIME);

DROP TABLE IF EXISTS services;
CREATE TABLE services (
		servicecode VARCHAR(10),
		description VARCHAR(200),
		nextservice VARCHAR(10));
		
DROP TABLE IF EXISTS servicelines;
CREATE TABLE servicelines (
		servicecode VARCHAR(10),
		placecode VARCHAR(10),
		scheduledarrivaltime TIME,
		scheduleddeparturetime TIME,
		trackcode VARCHAR(10),
		stop BOOLEAN);
        
DROP TABLE IF EXISTS options;
CREATE TABLE options (
        optionKey VARCHAR(30),
        optionValue VARCHAR(50));
     
--
-- ################################### OPTIONS ###################################
--

INSERT INTO options VALUES ("timeFactor", "5");
INSERT INTO options VALUES ("currentTime","06:00:00");
INSERT INTO options VALUES ("warningSpeed", "8.3");
INSERT INTO options VALUES ("defaultMaxSpeed", "18");
INSERT INTO options VALUES ("defaultMinimumStopTime", "30");

--
-- ################################### TRACKITEMS ###################################
--

-- BANK PLATFORM 7
INSERT INTO trackitems (tiid, titype, x, y)       		VALUES (1000000, "E", 0, 100);        
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (71, "71", "SB", 60, 100, 1);
INSERT INTO trackitems (tiid, titype, x, y, xf, yf, realLength, xn, yn, xr, yr, placecode, trackcode) 
		VALUES (7, "LP", 60, 100, 130, 100, 80, 10, 105, 129, 125, "BNK", "7");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (72, "72", "S", 130, 100, 0);

-- BANK PLATFORM 8
INSERT INTO trackitems (tiid, titype, x, y)       		VALUES (601, "E", 0, 150);        
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (81, "81", "SB", 60, 150, 1);
INSERT INTO trackitems (tiid, titype, x, y, xf, yf, realLength, xn, yn, xr, yr, placecode, trackcode) 
		VALUES (8, "LP", 60, 150, 130, 150, 80, 10, 125, 129, 145, "BNK", "8");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (82, "82", "S", 130, 150, 0);

-- BANK CROSSOVER
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (511, "P", 201, 195, 100, -5, 0, 5, 0, 5, 5);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (521, "P", 202, 195, 150, -5, 0, 5, 0, 5, -5);
INSERT INTO trackitems (tiid, titype, ptiid, ntiid, x, y, xf, yf, conflicttiid)    
		VALUES (201, "L", 511, 522, 200, 105, 240, 145, 202);
INSERT INTO trackitems (tiid, titype, ptiid, ntiid, x, y, xf, yf) 	VALUES (202, "L", 521, 512, 200, 145, 240, 105);
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 200, 100, 240, 100);
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 200, 150, 240, 150);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (512, "P", 202, 245, 100, 5, 0, -5, 0, -5, 5);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (522, "P", 201, 245, 150, 5, 0, -5, 0, -5, -5);

-- BANK->WATERLOO LINE
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 250, 100, 450, 100, 700);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (73, "73", "S", 450, 100, 0);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 510, 100, 700, 100, 700);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (74, "74", "S", 700, 100, 0);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 760, 100, 950, 100, 700);

-- WATERLOO->BANK LINE
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (83, "83", "S", 310, 150, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 310, 150, 450, 150, 700);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (84, "84", "S", 510, 150, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 510, 150, 700, 150, 700);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (85, "85", "S", 760, 150, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 760, 150, 890, 150, 700);

-- WATERLOO PLATFORM 26
INSERT INTO trackitems (titype, x, y, xf, yf, realLength, xn, yn, xr, yr, placecode, trackcode) 
		VALUES ("LP", 950, 100, 1020, 100, 80, 950, 80, 1019, 95, "WTL", "26");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (75, "75", "S", 1020, 100, 0);

-- WATERLOO PLATFORM 25
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (86, "86", "S", 950, 150, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, realLength, xn, yn, xr, yr, placecode, trackcode) 
		VALUES ("LP", 950, 150, 1020, 150, 80, 950, 155, 1019, 170, "WTL", "25");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (87, "87", "S", 1020, 150, 0);

-- DEPOT - TRACK 26
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1080, 100, 1100, 100);
INSERT INTO trackitems (tiid, titype, ntiid, x, y, xf, yf)    VALUES (203, "L", 513, 1100, 100, 1120, 120);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (513, "P", 203, 1125, 125, 5, 0, -5, 5, -5, -5);

-- DEPOT - TRACK 25
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1080, 150, 1090, 150);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (523, "P", 204, 1095, 150, -5, 0, 5, 0, 5, 5);
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1100, 150, 1120, 130);

-- DEPOT - TRACK 3
INSERT INTO trackitems (tiid, titype, ptiid, x, y, xf, yf)    VALUES (204, "L", 523, 1100, 155, 1120, 175);
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1120, 175, 1125, 175);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (531, "P", 207, 1130, 175, -5, 0, 5, 0, 5, 5);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 1135, 175, 1155, 175, 70);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (31, "31", "S", 1215, 175, 1);
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1215, 175, 1260, 175);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (32, "32", "SB", 1260, 175, 0);
INSERT INTO trackitems (titype, x, y)       	 VALUES ("E", 1320, 175);               

-- DEPOT - TRACK 4
INSERT INTO trackitems (tiid, titype, ptiid, x, y, xf, yf)    VALUES (207, "L", 531, 1135, 180, 1155, 200);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (41, "41", "S", 1215, 200, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength)    VALUES ("L", 1215, 200, 1260, 200, 70);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (42, "42", "SB", 1260, 200, 0);
INSERT INTO trackitems (titype, x, y)       	 VALUES ("E", 1320, 200);               


-- DEPOT - TRACK 5
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1130, 125, 1145, 125);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (551, "P", 205, 1150, 125, -5, 0, 5, 0, 5, -5);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (51, "51", "S", 1215, 125, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, placecode, trackcode)    VALUES ("L", 1215, 125, 1300, 125, "DPT", "5");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (52, "52", "SB", 1300, 125, 0);
INSERT INTO trackitems (titype, x, y)       				 VALUES ("E", 1360, 125);               

-- DEPOT - TRACK 6
INSERT INTO trackitems (tiid, titype, ptiid, x, y, xf, yf)    VALUES (205, "L", 551, 1155, 120, 1175, 100);
INSERT INTO trackitems (titype, x, y, xf, yf)    VALUES ("L", 1175, 100, 1180, 100);
INSERT INTO trackitems (tiid, titype, rtiid, x, y, xf, yf, xn, yn, xr, yr) 
        VALUES (561, "P", 206, 1185, 100, -5, 0, 5, 0, 5, -5);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (61, "61", "S", 1250, 100, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength, placecode, trackcode)    
		VALUES ("L", 1250, 100, 1300, 100, 80, "DPT", "6");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (62, "62", "SB", 1300, 100, 0);
INSERT INTO trackitems (titype, x, y)       	 VALUES ("E", 1360, 100);               

-- DEPOT - TRACK 7
INSERT INTO trackitems (tiid, titype, ptiid, x, y, xf, yf)    VALUES (206, "L", 561, 1190, 95, 1210, 75);
INSERT INTO trackitems (tiid, name, titype, x, y, reverse)       VALUES (76, "76", "S", 1270, 75, 1);
INSERT INTO trackitems (titype, x, y, xf, yf, reallength, placecode, trackcode)    
		VALUES ("L", 1270, 75, 1300, 75, 80, "DPT", "7");
INSERT INTO trackitems (tiid, name, titype, x, y, reverse, timersw, timerwc)       VALUES (77, "77", "ST", 1300, 75, 0, 2.0, 1.0);
INSERT INTO trackitems (titype, x, y)       	 VALUES ("E", 1360, 75);               

--
-- ################################### PLACES ###################################
--
     
INSERT INTO trackitems (tiid, titype, placecode, name, x, y) VALUES (1, "A", "BNK", "BANK", 60, 50);
INSERT INTO trackitems (tiid, titype, placecode, name, x, y) VALUES (2, "A", "WTL", "WATERLOO", 950, 50);
INSERT INTO trackitems (tiid, titype, placecode, name, x, y) VALUES (3, "A", "DPT", "DEPOT", 1250, 50);

--
-- ################################### ROUTES ###################################
--

-- BANK->WATERLOO ROUTES
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (1, 72, 73);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (101, 82, 73);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (2, 73, 74);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (3, 74, 75);

-- WATERLOO->BANK ROUTES
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (51, 86, 85);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (52, 85, 84);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (53, 84, 83);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (54, 83, 81);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (102, 83, 71);

-- DEPOT ROUTES
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (201, 75, 77);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (202, 75, 62);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (203, 75, 52);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (204, 87, 77);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (205, 87, 62);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (206, 87, 52);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (207, 76, 86);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (208, 61, 86);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (209, 51, 86);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (210, 87, 32);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (211, 87, 42);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (212, 31, 86);
INSERT INTO routes (routenum, beginsignal, endsignal) VALUES (213, 41, 86);

--
-- ################################### DIRECTIONS ###################################
--
        
INSERT INTO directions VALUES (101, 521, 1);
INSERT INTO directions VALUES (102, 522, 1);
INSERT INTO directions VALUES (201, 551, 1);
INSERT INTO directions VALUES (201, 561, 1);
INSERT INTO directions VALUES (202, 551, 1);
INSERT INTO directions VALUES (204, 551, 1);
INSERT INTO directions VALUES (204, 561, 1);
INSERT INTO directions VALUES (205, 551, 1);
INSERT INTO directions VALUES (210, 523, 1);
INSERT INTO directions VALUES (211, 523, 1);
INSERT INTO directions VALUES (211, 531, 1);

--
-- ################################### ROUTE CONFLICTS ###################################
--
        
INSERT INTO routeconflicts VALUES (101, 102);

--
-- ################################### TRAIN TYPES ###################################
--


INSERT INTO traintypes VALUES ("UT", "Underground train", 25.0, 0.5, 0.5, 1.5, 70);
--
-- ################################### TRAINS ###################################
--

INSERT INTO trains VALUES ("BW01", "UT", 0.0, 0.0, 7, 71, 79, "06:00:00");
INSERT INTO trains VALUES ("BW02", "UT", 0.0, 0.0, 8, 81, 79, "06:00:00");

--
-- ################################### SERVICES ###################################
--

INSERT INTO services VALUES ("BW01", "First BANK->WATERLOO service", "WB01");
INSERT INTO services VALUES ("BW02", "Second BANK->WATERLOO service", "");
INSERT INTO services VALUES ("BW03", "Third BANK->WATERLOO service", "");
INSERT INTO services VALUES ("WB01", "First WATERLOO->BANK service", "");
 
--
-- ################################### SERVICE LINES ###################################
--
INSERT INTO servicelines VALUES ("BW01", "BNK", "06:00:00", "06:00:30", "7", 1);
INSERT INTO servicelines VALUES ("BW01", "WTL", "06:03:00", "06:04:30", "25", 1);
INSERT INTO servicelines VALUES ("BW01", "DPT", "06:05:30", "06:06:00", "5", 1);
INSERT INTO servicelines VALUES ("BW02", "BNK", "06:00:00", "06:05:00", "8", 1);
INSERT INTO servicelines VALUES ("BW02", "WTL", "06:08:30", "06:09:00", "26", 1);
INSERT INTO servicelines VALUES ("BW03", "BNK", "06:00:00", "06:10:30", "7", 1);
INSERT INTO servicelines VALUES ("BW03", "WTL", "06:02:30", "06:13:30", "25", 1);
INSERT INTO servicelines VALUES ("BW03", "DPT", "06:04:30", "06:15:00", "5", 1);
INSERT INTO servicelines VALUES ("WB01", "WTL", "06:06:30", "06:08:00", "26", 1);
INSERT INTO servicelines VALUES ("WB01", "BNK", "06:10:30", "06:11:00", "7", 1);
 