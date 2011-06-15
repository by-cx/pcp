CREATE VIEW mailboxes AS SELECT e.login||'@'||d.name AS email,password,uid,gid,homedir,d.name||'/'||e.login||'/' AS maildir,homedir||'/'||d.name||'/'||e.login||'/' AS dir,e.login AS name FROM emails_email e,domains_domain d WHERE e.domain_id = d.id;
-- CREATE VIEW redirects AS SELECT r.alias AS alias, e.login||'@'||d.name AS email FROM emails_redirect r,emails_email e,domains_domain d WHERE r.email_id = e.id AND e.domain_id = d.id;
CREATE VIEW redirects AS SELECT alias,email FROM emails_redirect;
-- CREATE VIEW balance AS SELECT u.id AS user_id, u.username AS username, SUM(i.cash) AS incomes, SUM(b.price) AS bills, SUM(i.cash)-SUM(b.price) AS "sum" FROM auth_user u, bills_bill b, bills_income i WHERE u.id = b.user_id AND u.id = i.user_id  GROUP BY u.id, u.username;

CREATE VIEW balance AS
SELECT u.id AS user_id,
       u.username AS username,
       COALESCE((SELECT SUM(cash) FROM bills_income WHERE user_id = u.id),0) AS incomes,
       COALESCE((SELECT SUM(price) FROM bills_bill WHERE user_id = u.id),0) AS bills,
       COALESCE((SELECT SUM(cash) FROM bills_income WHERE user_id = u.id),0)-COALESCE((SELECT SUM(price) FROM bills_bill WHERE user_id = u.id),0) AS "sum"
FROM auth_user u
GROUP BY user_id, username;
