-- Read these lines in a SQLite database browser or use sql_tasks.py.
-- First start app.py once so notices.db exists.
SELECT * FROM notices;
SELECT id, title, category FROM notices;
SELECT * FROM notices WHERE category = 'Technology';
SELECT COUNT(*) AS number_of_notices FROM notices;
SELECT category, COUNT(*) FROM notices GROUP BY category;
SELECT * FROM notices ORDER BY id DESC LIMIT 1;
-- CHALLENGE: Create a new SELECT using WHERE and ORDER BY.
