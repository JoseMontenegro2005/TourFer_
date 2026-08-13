USE usuarios_db;

DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS roles;

CREATE TABLE roles (
    id INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

INSERT INTO roles (id, nombre) VALUES (1, 'Admin'), (2, 'Cliente');

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rol_id INT NOT NULL DEFAULT 2, 
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

INSERT INTO `usuarios` (`id`, `nombre`, `email`, `password`, `rol_id`) VALUES
(101, 'Ana Pérez', 'ana.perez@email.com', '$2b$12$0TPh9qxvO5hO1wVjVHZ.beiYi8AkScl2UOEdGf7xqYlZghWhq7NHW', 2),
(102, 'Juan Rodríguez', 'juan.rodriguez@email.com', '$2b$12$wHHKAhXLbDtSBqTkDgGuFujk8OjGHEGnEsF1kTQ11MwUZTBzgCHsm', 2),
(103, 'Lucía Gómez', 'lucia.gomez@email.com', '$2b$12$46VNCjur9AUrVEsBOFK98eW0xeZj51UzMycXGSHcy97gYO6i22HD2', 2),
(104, 'Manuel Fernandez', 'mf@email.com', '$2b$12$Nw4DS/O2gygau6nA6.hVq.iBb92wk4m1KRY/gDuKydT52nPt62M52', 2),
(105, 'Jose Montenegro', 'jm@email.com', '$2b$12$nKqWAcjelSXRZ9UJDsev7.w21/J1LDU0xwjbVrmJ0510BAMC1Qv6a', 1);