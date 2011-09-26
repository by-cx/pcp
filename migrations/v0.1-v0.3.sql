----------------
-- Web server --
----------------

-- add domains

ALTER TABLE apacheconf_site ADD COLUMN "domains" varchar(1024);

-- move data serverName + serverAlias

UPDATE apacheconf_site s SET domains = "serverName"||' '||"serverAlias";

-- drop serverName

ALTER TABLE apacheconf_site DROP COLUMN "serverName";

-- drop serverAlias

ALTER TABLE apacheconf_site DROP COLUMN "serverAlias";

-- add type

ALTER TABLE apacheconf_site ADD COLUMN "type" varchar(20) DEFAULT 'static';

-- decide if its php/wsgi/static and save to type

UPDATE apacheconf_site s SET type = 'php' WHERE php = 't';
UPDATE apacheconf_site s SET type = 'uwsgi' WHERE id = (SELECT site_id FROM apacheconf_wsgi WHERE uwsgi = 't' AND s.id = site_id);
UPDATE apacheconf_site s SET type = 'modwsgi' WHERE id = (SELECT site_id FROM apacheconf_wsgi WHERE uwsgi = 'f' AND s.id = site_id);

-- drop php

ALTER TABLE apacheconf_site DROP COLUMN php;

-- drop ipv4

ALTER TABLE apacheconf_site DROP COLUMN ipv4;

-- drop ipv6

ALTER TABLE apacheconf_site DROP COLUMN ipv6;

-- add script

ALTER TABLE apacheconf_site ADD COLUMN script varchar(100) DEFAULT '';

-- move from wsgi table

UPDATE apacheconf_site s SET script = (SELECT script FROM apacheconf_wsgi WHERE site_id = s.id);

-- add processes

ALTER TABLE apacheconf_site ADD COLUMN "processes" integer DEFAULT 1;

-- move from wsgi table

UPDATE apacheconf_site s SET processes = (SELECT processes FROM apacheconf_wsgi WHERE site_id = s.id);

-- add threads

ALTER TABLE apacheconf_site ADD COLUMN "threads" integer DEFAULT 5;

-- move from wsgi table

UPDATE apacheconf_site s SET threads = (SELECT threads FROM apacheconf_wsgi WHERE site_id = s.id);

-- add virtualenv

ALTER TABLE apacheconf_site ADD COLUMN "virtualenv" varchar(100) DEFAULT '';

-- move from wsgi table

UPDATE apacheconf_site s SET virtualenv = (SELECT virtualenv FROM apacheconf_wsgi WHERE site_id = s.id);

-- add static

ALTER TABLE apacheconf_site ADD COLUMN "static" text DEFAULT '';

-- move from wsgi table

UPDATE apacheconf_site s SET static = (SELECT static FROM apacheconf_wsgi WHERE site_id = s.id);

-- add python_path

ALTER TABLE apacheconf_site ADD COLUMN "python_path" text DEFAULT '';

-- move from wsgi table

UPDATE apacheconf_site s SET python_path = (SELECT python_path FROM apacheconf_wsgi WHERE site_id = s.id);

-- add allow_ips

ALTER TABLE apacheconf_site ADD COLUMN "allow_ips" text DEFAULT '';

-- move from wsgi table

UPDATE apacheconf_site s SET allow_ips = (SELECT allow_ips FROM apacheconf_wsgi WHERE site_id = s.id);

-- add deny_ips

ALTER TABLE apacheconf_site ADD COLUMN "deny_ips" text DEFAULT '';

-- add extra

ALTER TABLE apacheconf_site ADD COLUMN "extra" text DEFAULT '';

-- move custom

UPDATE apacheconf_site s SET extra = (SELECT conf FROM apacheconf_custom WHERE site_id = s.id);

-- set not null

ALTER TABLE apacheconf_site ALTER COLUMN domains SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN type SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN script SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN processes SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN threads SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN virtualenv SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN static SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN python_path SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN allow_ips SET NOT NULL;
ALTER TABLE apacheconf_site ALTER COLUMN deny_ips SET NOT NULL;

-- drop wsgi

DROP TABLE apacheconf_wsgi;

-- drop custom

DROP TABLE apacheconf_custom;

-- drop aliases

DROP TABLE apacheconf_alias;

---------------
-- Databases --
---------------

ALTER TABLE pgs_pgsql ADD CONSTRAINT pgsql_dbname_unique UNIQUE (dbname);
ALTER TABLE mysql_mysqldb ADD CONSTRAINT mysql_dbname_unique UNIQUE (dbname);

