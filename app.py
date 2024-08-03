from flask import Flask,session,request,render_template,url_for,redirect,flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'PI_3'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)
app.secret_key = 'mysecretkey'


@app.route('/')
def home():
   print("Session:", session)
   return render_template('index.html')
def principal():
    return render_template('index.html')

@app.route('/inicioS', methods=['GET', 'POST'])
def inicioS():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Consulta para obtener el usuario por nombre de usuario
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id_nombre FROM nombres WHERE nombre = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            user_id = user[0]  # ID del usuario

            # Consulta para obtener la clave foránea (persona_id) relacionada con el usuario
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT id_persona FROM personas WHERE id_nombre = %s', (user_id,))
            persona_id = cursor.fetchone()
            cursor.close()

            if persona_id:
                persona_id_value = persona_id[0]  # ID de la persona

                # Consulta para obtener la contraseña del usuario encontrado
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT password FROM profesionales WHERE id_persona = %s', (persona_id_value,))
                stored_password = cursor.fetchone()
                cursor.close()

                if stored_password:
                    stored_password_plain = stored_password[0]  # Contraseña almacenada

                    # Verifica la contraseña proporcionada contra la almacenada
                    if stored_password_plain == password:
                        session['username'] = username
                        session['logged_in'] = True
                        return redirect(url_for('perfil'))
                    else:
                        flash('Contraseña incorrecta. Inténtalo de nuevo.')
                else:
                    flash('Usuario no encontrado. Inténtalo de nuevo.')
            else:
                flash('Usuario no encontrado. Inténtalo de nuevo.')
        else:
            flash('Usuario no encontrado. Inténtalo de nuevo.')

    return render_template('inicioS.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    if 'username' in session:
        username = session['username']

        if request.method == 'POST':
            # Si se envía el formulario, actualiza los datos del perfil
            nombre = request.form['txtNombre']
            apellido_paterno = request.form['txtApellidoPaterno']
            apellido_materno = request.form['txtApellidoMaterno']
            genero = request.form['txtGenero']
            FechaNacimiento = request.form['txtFechaNacimiento']
            telefono = request.form['txtTelefono']
            email = request.form['txtEmail']
            especialidad = request.form['txtEspecialidad']
            descripcion_especialidad = request.form['txtDescripcionEspecialidad']
            cedula = request.form['txtCedula']
            password = request.form['txtPassword']

            cursor = mysql.connection.cursor()

            # Actualizar la tabla nombres
            cursor.execute('''
                UPDATE nombres
                SET nombre = %s, apellido_paterno = %s, apellido_materno = %s
                WHERE nombre = %s
            ''', (nombre, apellido_paterno, apellido_materno, username))

            # Actualizar la tabla personas
            cursor.execute('''
                UPDATE personas
                SET telefono = %s, email = %s, Fecha_nacimiento = %s, id_genero = (SELECT id_genero FROM generos WHERE genero = %s)
                WHERE id_nombre = (SELECT id_nombre FROM nombres WHERE nombre = %s)
            ''', (telefono, email, FechaNacimiento, genero, nombre))

            # Actualizar la tabla profesionales
            cursor.execute('''
                UPDATE profesionales
                SET cedula = %s, password = %s
                WHERE id_persona = (SELECT id_persona FROM personas WHERE id_nombre = (SELECT id_nombre FROM nombres WHERE nombre = %s))
            ''', (cedula, password, nombre))

            mysql.connection.commit()
            cursor.close()

            flash('Datos actualizados correctamente')
            return redirect(url_for('perfil'))

        # Consulta para obtener el perfil del usuario incluyendo genero y Fecha_nacimiento
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT n.nombre, n.apellido_paterno, n.apellido_materno, 
                   p.telefono, p.email, p.Fecha_nacimiento, g.genero, 
                   e.nombre AS especialidad, e.descripcion AS descripcion_especialidad,
                   pr.cedula, pr.password
            FROM nombres n
            JOIN personas p ON n.id_nombre = p.id_nombre
            JOIN profesionales pr ON p.id_persona = pr.id_persona
            JOIN especialidades e ON pr.id_especialidad = e.id_especialidad
            JOIN generos g ON p.id_genero = g.id_genero
            WHERE n.nombre = %s
        ''', (username,))
        profile_data = cursor.fetchone()
        cursor.close()

        if profile_data:
            # Descompón los datos en variables
            nombre, apellido_paterno, apellido_materno, telefono, email, Fecha_nacimiento, genero, especialidad, descripcion_especialidad, cedula, password = profile_data
            
            # Pasa los datos a la plantilla
            return render_template('perfil.html', nombre=nombre, apellido_paterno=apellido_paterno, 
                                   apellido_materno=apellido_materno, telefono=telefono, 
                                   email=email, Fecha_nacimiento=Fecha_nacimiento, genero=genero,
                                   especialidad=especialidad, descripcion_especialidad=descripcion_especialidad, 
                                   cedula=cedula, password=password)
        else:
            flash('Datos del perfil no encontrados.')
            return redirect(url_for('inicioS'))
    else:
        return redirect(url_for('inicioS'))

@app.route('/delete_profile', methods=['GET'])
def delete_profile():
    if not session.get('logged_in'):
        return redirect(url_for('home'))

    if 'username' in session:
        username = session['username']

        cursor = mysql.connection.cursor()

        # Elimina la entrada de 'profesionales'
        cursor.execute('''
            DELETE FROM profesionales
            WHERE id_persona = (SELECT id_persona FROM personas WHERE id_nombre = (SELECT id_nombre FROM nombres WHERE nombre = %s))
        ''', (username,))

        # Elimina la entrada de 'personas'
        cursor.execute('''
            DELETE FROM personas
            WHERE id_nombre = (SELECT id_nombre FROM nombres WHERE nombre = %s)
        ''', (username,))

        # Elimina la entrada de 'nombres'
        cursor.execute('''
            DELETE FROM nombres
            WHERE nombre = %s
        ''', (username,))

        mysql.connection.commit()
        cursor.close()

        # Cierra la sesión del usuario
        session.pop('logged_in', None)
        session.pop('username', None)

        flash('Perfil eliminado correctamente')
        return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/directorio')
def directorio():
   if not session.get('logged_in'):
        return redirect(url_for('home'))
   return render_template('directorioM.html')

@app.route('/perfilMedico')
def perfilMedico():
   if not session.get('logged_in'):
        return redirect(url_for('home'))
   return render_template('perfilMed.html')

@app.route('/registroMedico')
def registroMedico():
   return render_template('registroMed.html')

@app.route('/registroPaciente')
def registroPaciente():
   return render_template('registro.html')

@app.route('/registrOp')
def registrOp():
   return render_template('registrOp.html')

@app.route('/test')
def test():
   if not session.get('logged_in'):
        return redirect(url_for('home'))
   return render_template('test.html')

@app.route('/respuestas')
def respuestas():
   if not session.get('logged_in'):
        return redirect(url_for('home'))
   return render_template('respuestas.html')

@app.route('/editar/<id>')
def editar(id):
     cur= mysql.connection.cursor()
     cur.execute('select * from T_psicologos where ID_psicologo=%s',[id])
     psi= cur.fetchone()
     return render_template ('perfilMed.html', albums = psi)

@app.route('/guardarMedico', methods=['POST'])
def guardarMedico():
    if request.method == 'POST':
        # Llamado a los datos del formulario
        FNombre = request.form['txtNombre']
        FApellidoPaterno = request.form['txtApellidoPaterno']
        FApellidoMaterno = request.form['txtApellidoMaterno']
        FGenero = request.form['txtGenero']
        FFechaNacimiento = request.form['txtFechaNacimiento']
        FTelefono = request.form['txtTelefono']
        FEmail = request.form['txtEmail']
        FEspecialidad = request.form['txtEspecialidad']
        FDescripcionEspecialidad = request.form['txtDescripcionEspecialidad']
        FCedula = request.form['txtCedula']
        Password = request.form['txtPassword']
        
        # Con un cursor se ingresan los datos a la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO nombres (nombre, apellido_paterno, apellido_materno) VALUES (%s, %s, %s)',
                       (FNombre, FApellidoPaterno, FApellidoMaterno))
        id_nombre = cursor.lastrowid  # Esta línea de código sirve para llamar al id del último registro realizado en la tabla
        cursor.execute('INSERT INTO generos (genero) VALUES (%s)', (FGenero,))
        id_genero = cursor.lastrowid
        cursor.execute('INSERT INTO personas (id_nombre, id_genero, fecha_nacimiento, telefono, email) VALUES (%s, %s, %s, %s, %s)',
                       (id_nombre, id_genero, FFechaNacimiento, FTelefono, FEmail))
        id_persona = cursor.lastrowid
        cursor.execute('INSERT INTO especialidades (nombre, descripcion) VALUES (%s, %s)',
                       (FEspecialidad, FDescripcionEspecialidad))
        id_especialidad = cursor.lastrowid
        cursor.execute('INSERT INTO profesionales (id_persona, id_especialidad, cedula, password) VALUES (%s, %s, %s, %s)', 
                       (id_persona, id_especialidad, FCedula, Password))
        mysql.connection.commit()
        flash('Registro guardado correctamente')  # El mensaje del registro al momento de guardar
        return redirect(url_for('registroMedico'))  # Redirige el mensaje a la página


@app.route('/guardarPaciente',methods=['POST'])
def guardarPaciente():

    if request.method== 'POST':
         FNombre=request.form['txtNombre']
         FTelefono=request.form['txtTelefono']
         FUsuario=request.form['txtUsuario']
         FPassword=request.form['txtPassword']
         
         cursor = mysql.connection.cursor()
         cursor.execute('insert into T_pacientes(Nombre_Completo,Telefono,Usuario,Password) values(%s,%s,%s,%s)', (FNombre,FTelefono,FUsuario,FPassword))
         mysql.connection.commit()
         flash('Registro guardado correctamente')
         return redirect(url_for('registroPaciente'))    


if __name__ == '__main__':
  app.run(port=3000,debug=True)


