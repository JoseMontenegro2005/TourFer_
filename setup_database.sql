DROP USER IF EXISTS 'user_catalogo'@'%';
DROP USER IF EXISTS 'user_reservas'@'%';
DROP USER IF EXISTS 'user_usuarios'@'%';

CREATE USER IF NOT EXISTS 'user_catalogo'@'%' IDENTIFIED BY 'tourpass123';
CREATE USER IF NOT EXISTS 'user_reservas'@'%' IDENTIFIED BY 'reservaspass456';
CREATE USER IF NOT EXISTS 'user_usuarios'@'%' IDENTIFIED BY 'usuariospass789';


DROP DATABASE IF EXISTS catalogo_db;
DROP DATABASE IF EXISTS reservas_db;
DROP DATABASE IF EXISTS usuarios_db;

CREATE DATABASE catalogo_db;
CREATE DATABASE reservas_db;
CREATE DATABASE usuarios_db;


GRANT ALL PRIVILEGES ON catalogo_db.* TO 'user_catalogo'@'%';
GRANT ALL PRIVILEGES ON reservas_db.* TO 'user_reservas'@'%';
GRANT ALL PRIVILEGES ON usuarios_db.* TO 'user_usuarios'@'%';

FLUSH PRIVILEGES;

