-- Nessie
CREATE USER nessie WITH PASSWORD 'nessie';
GRANT ALL PRIVILEGES ON DATABASE nessie TO nessie;

-- Marquez
CREATE USER marquez WITH PASSWORD 'marquez';
GRANT ALL PRIVILEGES ON DATABASE marquez TO marquez;
