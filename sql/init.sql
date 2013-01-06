CREATE VIEW mailboxes AS SELECT e.login||'@'||d.name AS email,password,uid,gid,homedir,d.name||'/'||e.login||'/' AS maildir,homedir||'/'||d.name||'/'||e.login||'/' AS dir,e.login AS name FROM emails_email e,domains_domain d WHERE e.domain_id = d.id;

-- CREATE VIEW redirects AS SELECT r.alias AS alias, e.login||'@'||d.name AS email FROM emails_redirect r,emails_email e,domains_domain d WHERE r.email_id = e.id AND e.domain_id = d.id;
CREATE VIEW redirects AS SELECT alias,email FROM emails_redirect;
-- CREATE VIEW balance AS SELECT u.id AS user_id, u.username AS username, SUM(i.cash) AS incomes, SUM(b.price) AS bills, SUM(i.cash)-SUM(b.price) AS "sum" FROM auth_user u, bills_bill b, bills_income i WHERE u.id = b.user_id AND u.id = i.user_id  GROUP BY u.id, u.username;

CREATE VIEW email_pam AS SELECT e.password AS password,e.login||'@'||d.name AS user FROM emails_email e, domains_domain d WHERE e.domain_id = d.id;

CREATE VIEW mailboxes AS
  SELECT
    e.login||'@'||d.name AS email,
    password,
    100 AS uid,
    100 AS gid,
    '/var/www/' AS homedir,
    d.name||'/'||e.login||'/' AS maildir,
    '/var/www'||'/'||d.name||'/'||e.login||'/' AS dir,
    e.login AS name
  FROM
    emails_email e,
    emails_domain d
  WHERE
    e.domain_id = d.id;