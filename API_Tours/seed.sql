USE catalogo_db;

DROP TABLE IF EXISTS tours;
DROP TABLE IF EXISTS guias;

CREATE TABLE guias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    biografia TEXT,
    foto_url VARCHAR(255)
);

CREATE TABLE tours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    destino VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    duracion_horas DECIMAL(4, 1) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    cupos_disponibles INT NOT NULL,
    imagen_url VARCHAR(255),
    guia_id INT,
    FOREIGN KEY (guia_id) REFERENCES guias(id) ON DELETE SET NULL
);

INSERT INTO guias (id, nombre, email, telefono, biografia, foto_url) VALUES
(1, 'Carlos Castaño', 'carlos.castano@email.com', '3111234567', 'Experto en la cultura cafetera con más de 15 años de experiencia en el Eje Cafetero.', 'https://example.com/carlos_castano.jpg'),
(2, 'Isabella Rojas', 'isabella.rojas@email.com', '3128765432', 'Historiadora y apasionada por el arte colonial de Cartagena. Sus tours son una inmersión en la historia viva.', 'https://example.com/isabella_rojas.jpg'),
(3, 'Mateo Vargas', 'mateo.vargas@email.com', '3139876543', 'Biólogo y guía de naturaleza. Especializado en la biodiversidad de la Amazonía colombiana.', 'https://example.com/mateo_vargas.jpg'),
(4, 'Sofía Moreno', 'sofia.moreno@email.com', '3145551234', 'Antropóloga y experta en las culturas indígenas de la Sierra Nevada de Santa Marta.', 'https://example.com/sofia_moreno.jpg');

INSERT INTO tours (nombre, destino, descripcion, duracion_horas, precio, cupos_disponibles, imagen_url, guia_id) VALUES
('Ruta del Café Ancestral', 'Salento, Quindío', 'Un viaje interactivo desde la siembra del grano hasta la taza. Incluye degustación con un maestro cafetero.', 4.5, 150000, 15, 'https://example.com/tour_cafe.jpg', 1),
('Secretos de la Ciudad Amurallada', 'Cartagena, Bolívar', 'Descubre las leyendas de piratas, esclavos y héroes que se esconden en las calles coloniales de Cartagena.', 3.0, 95000, 20, 'https://example.com/tour_cartagena.jpg', 2),
('Aventura en la Selva Amazónica', 'Leticia, Amazonas', 'Caminata nocturna por la selva para descubrir su fauna y flora única, con un guía local experto.', 6.0, 350000, 8, 'https://example.com/tour_amazonas.jpg', 3),
('Misterios del Oro Precolombino', 'Bogotá, Cundinamarca', 'Visita guiada al Museo del Oro para entender el significado y la técnica de las antiguas culturas indígenas.', 2.5, 80000, 25, 'https://example.com/tour_oro.jpg', 2),
('Trekking a la Ciudad Perdida', 'Sierra Nevada de Santa Marta', 'Una expedición de 4 días a las ruinas de la antigua ciudad Tayrona. Una aventura física y espiritual.', 96.0, 1400000, 12, 'https://example.com/tour_ciudad_perdida.jpg', 4),
('Graffiti Tour en la Comuna 13', 'Medellín, Antioquia', 'Conoce la historia de transformación social de Medellín a través del arte urbano y el hip-hop.', 3.5, 75000, 30, 'https://example.com/tour_comuna13.jpg', 1),
('Avistamiento de Ballenas Jorobadas', 'Nuquí, Chocó', 'Excursión en lancha para presenciar el majestuoso espectáculo de las ballenas jorobadas en el Pacífico colombiano.', 4.0, 250000, 10, 'https://example.com/tour_ballenas.jpg', 3),
('Historia y Sabor en Popayán', 'Popayán, Cauca', 'Recorrido por el centro histórico de la "Ciudad Blanca" y degustación de su gastronomía, patrimonio de la UNESCO.', 3.0, 110000, 18, 'https://example.com/tour_popayan.jpg', 1),
('Cultura Wayúu en el Desierto', 'Cabo de la Vela, La Guajira', 'Convive con una comunidad Wayúu, aprende sobre sus tradiciones, su tejido y la mística del desierto.', 48.0, 850000, 6, 'https://example.com/tour_guajira.jpg', 4),
('Explorando el Valle de Cocora', 'Salento, Quindío', 'Caminata entre las palmas de cera más altas del mundo, un paisaje único y emblemático de Colombia.', 5.0, 120000, 20, 'https://example.com/tour_cocora.jpg', 1),
('Pasado Colonial de Villa de Leyva', 'Villa de Leyva, Boyacá', 'Un recorrido a pie por uno de los pueblos más hermosos de Colombia, visitando la Plaza Mayor y museos locales.', 3.5, 90000, 22, 'https://example.com/tour_villa.jpg', 2),
('El Río de los Siete Colores', 'La Macarena, Meta', 'Visita al espectacular Caño Cristales durante su temporada de colores. Una maravilla natural única en el mundo.', 72.0, 2500000, 10, 'https://example.com/tour_cano.jpg', 3),
('Parque Arqueológico de San Agustín', 'San Agustín, Huila', 'Explora las monumentales estatuas de piedra de una misteriosa civilización precolombina, Patrimonio de la Humanidad.', 8.0, 180000, 15, 'https://example.com/tour_agustin.jpg', 4),
('Noche de Estrellas en el Desierto', 'Desierto de la Tatacoa, Huila', 'Una noche de observación astronómica en uno de los mejores lugares de Colombia para ver las estrellas.', 3.0, 100000, 30, 'https://example.com/tour_tatacoa.jpg', 1),
('Clase de Salsa Caleña', 'Cali, Valle del Cauca', 'Sumérgete en la cultura de la capital mundial de la salsa con una clase intensiva para principiantes.', 2.0, 60000, 25, 'https://example.com/tour_salsa.jpg', 1);