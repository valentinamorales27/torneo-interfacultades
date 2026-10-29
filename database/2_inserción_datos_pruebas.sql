use torneo_interfacultades;

/*INSERCIÓN DE DATOS DE PRUEBA*/
/*Se asignaron IDs manualmente para que sea más sencillo crear las pruebas*/


/*Facultades*/
insert into facultad (id_facultad, nombre) values
(1, 'Ingenieria y Tecnologias'),
(2, 'Ciencias Empresariales'),
(3, 'Enfermería'),
(4, 'Agronomía'),
(5, 'Ciencias Sociales'),
(6, 'Ciencias y Tecnologia');

/*Torneo*/
insert into torneo (id_torneo, nombre, anio, semestre, fecha_inicio, fecha_fin, estado) values
(1, 'Torneo Interfacultades de Fútbol 5', 2026, 2, '2026-09-01', '2026-11-30', 'en curso');

/*Complejos*/
insert into complejo (id_complejo, nombre, direccion, departamento) values
(1, 'Complejo Santa María', 'Av. 18 de Julio 1893', 'Montevideo'),
(2, 'Complejo Los Bulevares', 'Av. Bulevar Artigas 2130', 'Montevideo'),
(3, 'Complejo El Rincón', 'Yaro 1240', 'Montevideo');

/*Turnos*/
insert into turno (id_turno, hora_inicio, hora_fin) values
(1, '18:00:00', '19:00:00'),
(2, '19:00:00', '20:00:00'),
(3, '20:00:00', '21:00:00'),
(4, '21:00:00', '22:00:00'),
(5, '22:00:00', '23:00:00');

/*Logins (usuarios)*/
insert into login (correo, contraseña, rol) values
('admin_torneo@gmail.com', 'admin1234', 'administrador'),
('planillero_torneo@gmail.com', 'planillero1234', 'planillero');

/*Jugadores*/
insert into jugador (ci, nombre, apellido, email, fecha_nacimiento, tipo, id_facultad) values
('12345672','Bruno','Pereira','bruno.pereira@gmail.com','2002-03-12','grado',1),
('12482969','Lucía','Morales','lucia.morales@gmail.com','2001-07-08','grado',1),
('12620252','Valentina','Méndez','valentina.mendez@gmail.com','2000-11-21','posgrado',1),
('12757546','Diego','Rodríguez','diego.rodriguez@gmail.com','1985-04-15','docente',1),
('12894833','Mariana','Sosa','mariana.sosa@gmail.com','1990-09-03','funcionario',1),

('13032127','Federico','López','federico.lopez@gmail.com','2002-01-19','grado',2),
('13169411','Camila','Fernández','camila.fernandez@gmail.com','2001-05-22','grado',2),
('13306700','Agustín','Montiel','agustin.montiel@gmail.com','1999-12-02','grado',2),
('13443990','Florencia','Vázquez','florencia.vazquez@gmail.com','1987-02-10','posgrado',2),
('13581281','Joaquín','Mora','joaquin.mora@gmail.com','1991-06-27','funcionario',2),

('13718577','Martín','Suárez','martin.suarez@gmail.com','2003-08-17','grado',3),
('13855864','Sofía','Fernández','sofia.fernandez@gmail.com','2002-10-04','grado',3),
('13993155','Mateo','Dinardi','mateo.dinardi@gmail.com','2000-02-14','grado',3),
('14130445','Nicolás','Cabrera','nicolas.cabrera@gmail.com','1982-01-30','docente',3),
('14267739','Carolina','Acosta','carolina.acosta@gmail.com','1993-12-11','docente',3),

('14405022','Pablo','Techera','pablo.techera@gmail.com','2001-04-06','grado',4),
('14542319','Renata','Olivera','renata.olivera@gmail.com','2002-06-18','posgrado',4),
('14679603','Santiago','Paz','santiago.paz@gmail.com','1998-09-25','posgrado',4),
('14816895','Camila','Viera','camila.viera@gmail.com','1984-03-09','docente',4),
('14954186','Facundo','Medina','facundo.medina@gmail.com','1992-07-13','funcionario',4),

('15091474','Valentina','Costa','valentina.costa@gmail.com','2003-02-20','grado',5),
('15228760','Ignacio','Lemos','ignacio.lemos@gmail.com','2001-11-16','grado',5),
('15366051','Julieta','Farías','julieta.farias@gmail.com','2000-05-01','grado',5),
('15503340','Gabriel','Correa','gabriel.correa@gmail.com','1986-08-29','grado',5),
('15640637','Micaela','Pintos','micaela.pintos@gmail.com','1994-10-07','posgrado',5),

('15777921','Emiliano','Reyes','emiliano.reyes@gmail.com','2002-12-13','grado',6),
('15915214','Bianca','Iglesias','bianca.iglesias@gmail.com','2001-03-26','posgrado',6),
('16052502','Rodrigo','Giménez','rodrigo.gimenez@gmail.com','1999-06-07','posgrado',6),
('16189799','Ana','Molina','ana.molina@gmail.com','1983-11-05','funcionario',6),
('16327082','Sebastián','Perdomo','sebastian.perdomo@gmail.com','1990-01-22','funcionario',6),

('16464378','Mateo','Silveira','mateo.silveira@gmail.com','2002-04-18','grado',1),
('16601665','Milagros','Bentancur','milagros.bentancur@gmail.com','2001-09-23','grado',2),
('16738950','Thiago','Sánchez','thiago.sanchez@gmail.com','2003-01-14','grado',3),
('16876244','Agustina','Pereira','agustina.pereira@gmail.com','2002-08-05','grado',4),
('17013532','Franco','Méndez','franco.mendez@gmail.com','2001-12-19','grado',5),
('17150820','Luciano','Fagúndez','luciano.fagundez@gmail.com','2002-06-11','grado',6);

/*Canchas*/
insert into cancha (nombre_cancha, id_complejo, superficie, techada) values
('Cancha S', 1, 'sintético', true),
('Cancha P', 1, 'parquet', true),
('Cancha S', 2, 'sintético', false),
('Cancha P', 2, 'sintético', false),
('Cancha S', 3, 'parquet', true),
('Cancha P', 3, 'sintético', false);

/*Equipos*/
insert into equipo (id_equipo, nombre, id_torneo, id_facultad, ci_capitan) values
(1, 'Los Nerds FC', 1, 1, '12345672'),
(2, 'Empresarios de la Plata', 1, 2, '13032127'),
(3, 'Salud FC', 1, 3, '13718577'),
(4, 'Los Toros', 1, 4, '14405022'),
(5, 'Sociales FC', 1, 5, '15091474'),
(6, 'FC Robots', 1, 6, '15777921');

/*Equipo_Jugador_Torneo*/
insert into equipo_jugador_torneo (id_equipo, ci_jugador, id_torneo, numero_camiseta) values
(1,'12345672',1,1),
(1,'12482969',1,2),
(1,'12620252',1,3),
(1,'12757546',1,4),
(1,'12894833',1,5),
(1,'16464378',1,6),

(2,'13032127',1,1),
(2,'13169411',1,2),
(2,'13306700',1,3),
(2,'13443990',1,4),
(2,'13581281',1,5),
(2,'16601665',1,6),

(3,'13718577',1,1),
(3,'13855864',1,2),
(3,'13993155',1,3),
(3,'14130445',1,4),
(3,'14267739',1,5),
(3,'16738950',1,6),

(4,'14405022',1,1),
(4,'14542319',1,2),
(4,'14679603',1,3),
(4,'14816895',1,4),
(4,'14954186',1,5),
(4,'16876244',1,6),

(5,'15091474',1,1),
(5,'15228760',1,2),
(5,'15366051',1,3),
(5,'15503340',1,4),
(5,'15640637',1,5),
(5,'17013532',1,6),

(6,'15777921',1,1),
(6,'15915214',1,2),
(6,'16052502',1,3),
(6,'16189799',1,4),
(6,'16327082',1,5),
(6,'17150820',1,6);

/*Partidos*/
insert into partido (id_partido, id_torneo, numero_fecha, id_equipo_local, id_equipo_visitante, dia, id_turno, nombre_cancha, id_complejo, estado) values
(1,1,1,1,2,'2026-10-01',1,'Cancha S',1,'jugado'),
(2,1,1,3,4,'2026-10-01',2,'Cancha P',1,'jugado'),
(3,1,1,5,6,'2026-10-01',3,'Cancha S',2,'jugado'),
(4,1,2,1,3,'2026-10-08',1,'Cancha P',1,'jugado'),
(5,1,2,2,5,'2026-10-08',2,'Cancha S',2,'jugado'),
(6,1,2,4,6,'2026-10-08',3,'Cancha S',3,'jugado'),
(7,1,3,1,4,'2026-10-15',1,'Cancha P',2,'jugado'),
(8,1,3,2,6,'2026-10-15',2,'Cancha P',3,'jugado'),
(9,1,3,3,5,'2026-10-15',3,'Cancha S',1,'jugado'),
(10,1,4,1,5,'2026-10-29',1,'Cancha S',3,'postergado'),
(11,1,4,2,4,'2026-10-29',2,'Cancha P',2,'cancelado'),
(12,1,4,3,6,'2026-10-29',3,'Cancha S',1,'programado'),
(13,1,5,1,6,'2026-11-05',1,'Cancha S',1,'programado'),
(14,1,5,2,3,'2026-11-05',2,'Cancha P',1,'programado'),
(15,1,5,4,5,'2026-11-05',3,'Cancha S',2,'programado');


/*Planillas*/
insert into planilla_partido (id_partido, ci_jugador, id_equipo) values
(1,'12345672',1),
(1,'12482969',1),
(1,'12620252',1),
(1,'12757546',1),
(1,'12894833',1),
(1,'13032127',2),
(1,'13169411',2),
(1,'13306700',2),
(1,'13443990',2),
(1,'13581281',2),

(2,'13718577',3),
(2,'13855864',3),
(2,'13993155',3),
(2,'14130445',3),
(2,'14267739',3),
(2,'14405022',4),
(2,'14542319',4),
(2,'14679603',4),
(2,'14816895',4),
(2,'14954186',4),

(3,'15091474',5),
(3,'15228760',5),
(3,'15366051',5),
(3,'15503340',5),
(3,'15640637',5),
(3,'15777921',6),
(3,'15915214',6),
(3,'16052502',6),
(3,'16189799',6),
(3,'16327082',6),

(4,'12345672',1),
(4,'12482969',1),
(4,'12620252',1),
(4,'12757546',1),
(4,'12894833',1),
(4,'13718577',3),
(4,'13855864',3),
(4,'13993155',3),
(4,'14130445',3),
(4,'14267739',3),

(5,'13032127',2),
(5,'13169411',2),
(5,'13306700',2),
(5,'13443990',2),
(5,'13581281',2),
(5,'15091474',5),
(5,'15228760',5),
(5,'15366051',5),
(5,'15503340',5),
(5,'15640637',5),

(6,'14405022',4),
(6,'14542319',4),
(6,'14679603',4),
(6,'14816895',4),
(6,'14954186',4),
(6,'15777921',6),
(6,'16052502',6),
(6,'16189799',6),
(6,'16327082',6),
(6,'17150820',6),

(7,'12345672',1),
(7,'12620252',1),
(7,'12757546',1),
(7,'12894833',1),
(7,'16464378',1),
(7,'14405022',4),
(7,'14542319',4),
(7,'14679603',4),
(7,'14816895',4),
(7,'14954186',4),

(8,'13032127',2),
(8,'13169411',2),
(8,'13306700',2),
(8,'13443990',2),
(8,'13581281',2),
(8,'15777921',6),
(8,'15915214',6),
(8,'16052502',6),
(8,'16189799',6),
(8,'16327082',6),

(9,'13718577',3),
(9,'13855864',3),
(9,'13993155',3),
(9,'14130445',3),
(9,'14267739',3),
(9,'15091474',5),
(9,'15228760',5),
(9,'15366051',5),
(9,'15503340',5),
(9,'15640637',5);

/*Goles*/
insert into gol (id_gol, id_partido, ci_jugador, minuto, autogol) values
(1,1,'12345672',5,false),
(2,1,'12482969',17,false),
(3,1,'13032127',28,false),
(4,2,'13718577',12,false),
(5,2,'14405022',20,false),
(6,3,'15777921',4,false),
(7,3,'15915214',14,false),
(8,3,'16052502',31,false),
(9,4,'13718577',8,false),
(10,4,'13855864',22,true),
(11,5,'13032127',3,false),
(12,5,'13169411',11,false),
(13,5,'13306700',25,false),
(14,5,'15091474',33,false),
(15,6,'14405022',15,false),
(16,6,'14542319',29,false),
(17,7,'12345672',19,false),
(18,8,'13032127',6,false),
(19,8,'13169411',24,false),
(20,8,'15777921',9,true),
(21,8,'15915214',30,false),
(22,9,'13718577',2,false),
(23,9,'13855864',10,false),
(24,9,'13993155',18,false),
(25,9,'13718577',26,false),
(26,9,'15091474',34,false);

/*Tarjetas*/
insert into tarjeta (id_tarjeta, id_partido, ci_jugador, minuto, color) values
(1,1,'12482969',15,'amarilla'),
(2,1,'13169411',21,'amarilla'),
(3,2,'13855864',17,'amarilla'),
(4,2,'14542319',23,'amarilla'),
(5,3,'15228760',12,'amarilla'),
(6,3,'15915214',27,'roja'),
(7,4,'12620252',19,'amarilla'),
(8,4,'13993155',24,'amarilla'),
(9,5,'13306700',16,'amarilla'),
(10,5,'15228760',30,'amarilla'),
(11,6,'14679603',18,'amarilla'),
(12,6,'16052502',25,'amarilla'),
(13,4,'12482969',30,'roja'),
(14,7,'14542319',28,'amarilla'),
(15,8,'13306700',13,'amarilla'),
(16,8,'15915214',32,'amarilla'),
(17,9,'13855864',14,'amarilla'),
(18,9,'15366051',20,'amarilla'),
(19,7,'14679603',28,'amarilla'),
(20,7,'14679603',32,'amarilla'),
(21, 7, '14679603', 32, 'roja');

/*Sanciones*/
insert into sancion_jugador (id_sancion, ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas) values
(1,'15915214',1,'roja',2,1),
(2,'12482969',1,'roja',3,1),
(3,'14679603',1,'acumulación de amarillas',4,1),
(4,'13306700',1,'disciplinaria',4,2);