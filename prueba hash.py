from flask import Flask,request,render_template,url_for,redirect,session,flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
password = '28022000'
hashed_password = generate_password_hash(password)
print("Contraseña hasheada:", hashed_password)