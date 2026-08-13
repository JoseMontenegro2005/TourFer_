USE reservas_db;

DROP TABLE IF EXISTS reservas;

CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tour_id INT NOT NULL, 
    usuario_id INT,
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cantidad_personas INT NOT NULL,
    costo_total DECIMAL(10, 2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Confirmada' CHECK (estado IN ('Pendiente', 'Confirmada', 'Cancelada')),

    FOREIGN KEY (usuario_id) REFERENCES usuarios_db.usuarios(id),
    FOREIGN KEY (tour_id) REFERENCES catalogo_db.tours(id)
);

INSERT INTO `reservas` (`id`, `tour_id`, `usuario_id`, `cantidad_personas`, `costo_total`, `estado`) VALUES
(1, 1, 101, 2, 300000.00, 'Confirmada'),
(2, 3, 102, 1, 350000.00, 'Confirmada'),
(6, 5, 104, 1, 1400000.00, 'Confirmada');