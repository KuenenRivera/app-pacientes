from flask import Flask, render_template, request, redirect, session
import sqlite3
import json
import os

# 🔥 CREAR BD AUTOMÁTICAMENTE EN LA NUBE
if not os.path.exists("database.db"):
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT,
        nombre TEXT,
        edad INTEGER,
        diagnostico TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dni TEXT,
        fecha TEXT,
        inr REAL,
        dosis TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        password TEXT,
        rol TEXT
    )
    """)

    # 🔥 USUARIOS INICIALES
    cur.execute("INSERT INTO roles VALUES (NULL,'doctor','123','doctor')")
    cur.execute("INSERT INTO roles VALUES (NULL,'paciente','123','paciente')")

    con.commit()
    con.close()

app = Flask(__name__)
app.secret_key = "clave_secreta"


def conectar():
    return sqlite3.connect("database.db")


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT * FROM roles WHERE usuario=? AND password=?",
                    (usuario, password))
        user = cur.fetchone()
        con.close()

        if user:
            session["usuario"] = usuario
            session["rol"] = user[3]

            if user[3] == "doctor":
                return redirect("/reporte")
            else:
                return redirect("/")
        else:
            return "Credenciales incorrectas"

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -------------------------
# PACIENTE (DNI)
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "usuario" not in session:
        return redirect("/login")

    if session["rol"] != "paciente":
        return "Acceso solo pacientes"

    if request.method == "POST":
        dni = request.form["dni"].strip()

        if not dni.isdigit():
            return "Error: El DNI solo debe contener números"

        if len(dni) != 8:
            return "Error: El DNI debe tener exactamente 8 dígitos"

        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT * FROM usuarios WHERE dni=?", (dni,))
        usuario = cur.fetchone()
        con.close()

        if usuario:
            return redirect(f"/edicion/{dni}")
        else:
            return redirect(f"/registro/{dni}")

    return render_template("index.html")


# -------------------------
# REGISTRO PACIENTE
# -------------------------
@app.route("/registro/<dni>", methods=["GET", "POST"])
def registro(dni):
    if "usuario" not in session or session["rol"] != "paciente":
        return redirect("/login")

    if request.method == "POST":
        nombre = request.form["nombre"]
        edad = request.form["edad"]
        diagnostico = request.form["diagnostico"]

        if not nombre or not edad or not diagnostico:
            return "Error: Complete todos los campos"

        con = conectar()
        cur = con.cursor()
        cur.execute("INSERT INTO usuarios VALUES (NULL,?,?,?,?)",
                    (dni, nombre, edad, diagnostico))
        con.commit()
        con.close()

        return redirect(f"/edicion/{dni}")

    return render_template("registro.html", dni=dni)


# -------------------------
# EDICIÓN (INR + DOSIS)
# -------------------------
@app.route("/edicion/<dni>", methods=["GET", "POST"])
def edicion(dni):
    if "usuario" not in session or session["rol"] != "paciente":
        return redirect("/login")

    if request.method == "POST":
        fecha = request.form.get("fecha")
        inr = request.form.get("inr")

        if not fecha or not inr:
            return "Error: Debe completar fecha e INR"

        dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]

        for dia in dias:
            if not request.form.get(dia):
                return f"Error: Falta seleccionar dosis en {dia}"

        dosis = {dia: request.form.get(dia) for dia in dias}

        con = conectar()
        cur = con.cursor()
        cur.execute("INSERT INTO registros VALUES (NULL,?,?,?,?)",
                    (dni, fecha, inr, json.dumps(dosis)))
        con.commit()
        con.close()

        return redirect("/")

    return render_template("edicion.html", dni=dni)


# -------------------------
# DOCTOR → REPORTE (🔥 FIX COMPLETO)
# -------------------------
@app.route("/reporte")
def reporte():
    if "usuario" not in session or session["rol"] != "doctor":
        return redirect("/login")

    con = conectar()
    cur = con.cursor()

    # 🔥 AQUÍ ESTÁ EL FIX IMPORTANTE (JOIN)
    cur.execute("""
        SELECT r.dni, u.nombre, r.fecha, r.inr, r.dosis
        FROM registros r
        LEFT JOIN usuarios u ON r.dni = u.dni
        ORDER BY r.fecha DESC
    """)

    filas = cur.fetchall()
    con.close()

    registros = []

    for f in filas:
        try:
            dosis = json.loads(f[4]) if f[4] else {}
        except:
            dosis = {}

        try:
            inr_valor = float(f[3]) if f[3] else 0
        except:
            inr_valor = 0

        registros.append({
            "dni": f[0],
            "nombre": f[1] if f[1] else "Sin nombre",
            "fecha": f[2],
            "inr": inr_valor,
            "dosis": dosis
        })

    return render_template("reporte.html", registros=registros)


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)