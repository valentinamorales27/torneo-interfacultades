drop database if exists torneo_interfacultades;
create database torneo_interfacultades;
use torneo_interfacultades;

/*CREACIÓN DE TABLAS*/

create table login(
    correo varchar(50) primary key,
    contraseña varchar(255) not null,
    rol enum('administrador', 'planillero') not null
);

create table facultad(
    id_facultad int auto_increment primary key,
    nombre varchar(50) not null unique /*no queremos que haya 2 facultades con el mismo nombre*/
);

create table torneo(
    id_torneo int auto_increment primary key,
    nombre varchar(50) not null,
    anio int not null,
    semestre int not null,
    fecha_inicio date not null,
    fecha_fin date not null,
    estado enum('inscripción', 'en curso', 'finalizado') not null,
    /*acá agregamos verificaciónes para que sean válidos*/
    check (semestre in (1,2)),
    check (anio>0),
    check (fecha_fin>=fecha_inicio),
    unique (anio,semestre) /*hay un solo torneo por semestre*/
);

create table complejo(
    id_complejo int auto_increment primary key,
    nombre varchar(50) not null,
    direccion varchar(100) not null,
    departamento varchar(50) not null
);

create table turno(
    id_turno int auto_increment primary key,
    hora_inicio time not null unique,/*no puede haber 2 turnos con misma hora de inicio/fin*/
    hora_fin time not null unique,
    /*validación de horas y duración del partido*/
    check(hora_fin=ADDTIME(hora_inicio, '01:00:00')),
    check(hora_inicio>='18:00:00'),
    check(hora_fin<='23:00:00')
);

create table jugador(
    ci varchar(8) primary key,
    nombre varchar(50) not null,
    apellido varchar(50) not null,
    email varchar(50) not null unique, /*no existen 2 emails iguales*/
    fecha_nacimiento date not null,
    tipo enum('grado', 'posgrado', 'docente', 'funcionario') not null,
    id_facultad int not null,
    foreign key (id_facultad) references facultad(id_facultad)

);
create table cancha(
    nombre_cancha varchar(50) not null,
    id_complejo int not null,
    superficie enum('sintético', 'parquet') not null,
    techada boolean not null,
    primary key (nombre_cancha, id_complejo), /*clave primaria compuesta*/
    foreign key (id_complejo) references complejo(id_complejo)
);

create table equipo(
    id_equipo int auto_increment primary key,
    nombre varchar(50) not null,
    id_torneo int not null,
    id_facultad int not null,
    ci_capitan varchar(8) not null,
    foreign key (id_facultad) references facultad(id_facultad),
    foreign key (id_torneo) references torneo(id_torneo),
    foreign key (ci_capitan) references jugador(ci),
    /*dejamos que una facultad pueda tener +1 equipo en un torneo*/
    unique(id_equipo, id_torneo) /*para clave foránea en equipo_jugador_torneo, para poder usarla bien debe ser único sino habría varios valores posibles*/
);

create table equipo_jugador_torneo(
    id_equipo int not null,
    ci_jugador varchar(8) not null,
    id_torneo int not null,
    numero_camiseta int not null,
    primary key (id_equipo,ci_jugador,id_torneo), /*clave primaria compuesta*/
    foreign key (id_equipo,id_torneo) references equipo(id_equipo, id_torneo),
    foreign key (ci_jugador) references jugador(ci),
    check(numero_camiseta>0), /*no número negativos*/
    unique (ci_jugador, id_torneo)
    /*
      un jugador solo puede aparecer 1 vez
      en el torneo ya que solo puede formar
      parte de 1 equipo
    */,
    unique (id_equipo, id_torneo, numero_camiseta) /*no puede haber 2 número de remera igual en 1 mismo equipo*/
);

create table partido(
    id_partido int auto_increment primary key,
    id_torneo int not null,
    numero_fecha int not null,
    id_equipo_local int not null,
    id_equipo_visitante int not null,
    dia date not null,
    id_turno int not null,
    nombre_cancha varchar(50) not null,
    id_complejo int not null,
    estado enum('programado', 'jugado', 'postergado', 'cancelado') not null default 'programado', /*si se agregó y no se especificó es porque está recién programado*/
    foreign key (id_torneo) references torneo(id_torneo),
    /*verificamos que además de estar en la tabla de equipos pertenezcan al torneo*/
    foreign key (id_equipo_local, id_torneo) references equipo(id_equipo, id_torneo),
    foreign key (id_equipo_visitante, id_torneo) references equipo(id_equipo, id_torneo),
    foreign key (id_turno) references turno(id_turno),
    foreign key (nombre_cancha, id_complejo) references cancha(nombre_cancha, id_complejo),
    /*verificamos que los equipos sean diferentes*/
    check (id_equipo_local<>id_equipo_visitante),
    /*verificamos que no haya fechas negativas ni 0*/
    check (numero_fecha>0),
    /*indexs: los agregamos para facilitar las consultas que se
      exigen en el obligatorio. Estas estructuras auxiliares ayudan
      a encontrar información de forma más rápida ya que no tiene que
      revisar fila por fila de la tabla
    */
    index idx_partido_torneo_fecha (id_torneo, numero_fecha),
    index idx_partido_local (id_equipo_local),
    index idx_partido_visitante (id_equipo_visitante),
    index idx_partido_cancha (dia, id_turno, id_complejo, nombre_cancha)
);

create table planilla_partido(
    id_partido int not null,
    ci_jugador varchar(8) not null,
    id_equipo int not null,
    primary key (id_partido, ci_jugador),
    foreign key (id_partido) references partido(id_partido),
    foreign key (ci_jugador) references jugador(ci),
    foreign key (id_equipo) references equipo(id_equipo)

);

create table gol(
    id_gol int auto_increment primary key ,
    id_partido int not null,
    ci_jugador varchar(8) not null,
    minuto int not null,
    autogol boolean not null default false, /*es verdadero si se aclara, sino es gol normal*/
    foreign key (id_partido, ci_jugador) references planilla_partido(id_partido, ci_jugador),
    check (minuto>=0) /*no aceptamos minutos negativos*/
);

create table tarjeta(
    id_tarjeta int auto_increment primary key ,
    id_partido int not null ,
    ci_jugador varchar(8) not null ,
    minuto int not null ,
    color enum('amarilla', 'roja') not null,
    foreign key (id_partido, ci_jugador) references planilla_partido(id_partido, ci_jugador),
    check(minuto>=0)
);

create table sancion_jugador(
    id_sancion int auto_increment primary key,
    ci_jugador varchar(8) not null,
    id_torneo int not null,
    motivo enum('roja', 'acumulación de amarillas', 'disciplinaria') not null,
    numero_fecha_inicio int not null,
    cantidad_fechas int not null,
    foreign key (ci_jugador) references jugador(ci),
    foreign key (id_torneo) references torneo(id_torneo),
    /*no números negativos*/
    check(numero_fecha_inicio>0),
    check(cantidad_fechas>0),
    index idx_sancion_jugador_torneo(ci_jugador, id_torneo)
);



