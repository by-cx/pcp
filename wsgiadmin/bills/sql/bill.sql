CREATE VIEW balance AS
SELECT u.id AS user_id,
       u.username AS username,
       COALESCE((SELECT SUM(cash) FROM bills_income WHERE user_id = u.id),0) AS incomes,
       COALESCE((SELECT SUM(price) FROM bills_bill WHERE user_id = u.id),0) AS bills,
       COALESCE((SELECT SUM(cash) FROM bills_income WHERE user_id = u.id),0)-COALESCE((SELECT SUM(price) FROM bills_bill WHERE user_id = u.id),0) AS "sum"
FROM auth_user u
GROUP BY user_id, username;
