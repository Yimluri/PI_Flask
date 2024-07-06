from flask import Flask,request,jsonify,render_template,flash,url_for,redirect

from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'proyectoi1'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)
app.secret_key = 'mysecretkey'

#ruta simple

@app.route('/')
def principal():
   return render_template('index.html')

@app.route('/inicioS')
def inicioS():
   return render_template('inicioS.html')

@app.route('/directorio')
def directorio():
   return render_template('directorioM.html')

@app.route('/perfilMedico')
def perfilMedico():
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
   return render_template('test.html')

@app.route('/respuestas')
def respuestas():
   return render_template('respuestas.html')

@app.route('/guardarMedico',methods=['POST'])
def guardarMedico():

    if request.method== 'POST':
         FNombre=request.form['txtNombre']
         FCedula=request.form['txtCedula']
         FTelefono=request.form['txtTelefono']
         FCorreo=request.form['txtCorreo']
         FPassword=request.form['txtPassword']
         
         cursor = mysql.connection.cursor()
         cursor.execute('insert into table_med(nombre,cedula,telefono,correo,password) values(%s,%s,%s,%s,%s)', (FNombre,FCedula,FTelefono,FCorreo,FPassword))
         mysql.connection.commit()
         flash('Registro guardado correctamente')
         return redirect(url_for('registroMedico'))


if __name__ == '__main__':
  app.run(port=3000,debug=True)


