from flask import Flask,request,jsonify,render_template

app = Flask (__name__)

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


if __name__ == '__main__':
  app.run(port=3000,debug=True)


