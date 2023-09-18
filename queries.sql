CREATE TABLE your_table (
    id SERIAL PRIMARY KEY,
    column_name VARCHAR(255)
);

INSERT INTO your_table (column_name) VALUES (%s);

UPDATE your_table SET column_name = %s WHERE id = %s;

DELETE FROM your_table WHERE id = %s;
