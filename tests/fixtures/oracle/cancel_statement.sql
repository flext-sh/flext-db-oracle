SELECT SUM(MOD(left_rows.id * right_rows.id, 17))
FROM (SELECT LEVEL id FROM dual CONNECT BY LEVEL <= 15000) left_rows
CROSS JOIN (SELECT LEVEL id FROM dual CONNECT BY LEVEL <= 15000) right_rows
