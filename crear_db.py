import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

# TABLA USUARIOS
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT,
    nombre TEXT,
    edad INTEGER,
    diagnostico TEXT
)
""")

# TABLA REGISTROS
cur.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT,
    fecha TEXT,
    inr REAL,
    dosis TEXT
)
""")

# TABLA LOGIN
cur.execute("""
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    password TEXT,
    rol TEXT
)
""")

# LIMPIAR Y CREAR SOLO 2 ROLES
cur.execute("DELETE FROM roles")

cur.execute("INSERT INTO roles (usuario,password,rol) VALUES ('doctor','123','doctor')")
cur.execute("INSERT INTO roles (usuario,password,rol) VALUES ('paciente','123','paciente')")

con.commit()
con.close()

print("BD lista")