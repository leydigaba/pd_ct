import pyrebase
import bcrypt  # Importar bcrypt para el hashing de contraseñas
import json

config = {
    "apiKey": "AIzaSyBJf1q8pBMRDbK1-QsCBOAlCFWlC7ehh1A",
    "authDomain": "babychatpediatras.firebaseapp.com",
    "databaseURL": "https://babychatpediatras-default-rtdb.firebaseio.com",
    "storageBucket": "babychatpediatras.firebasestorage.app"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()


def registrar_usuario(nombre, apellido1, apellido2, fecha_nacimiento, correo, licencia, password):
    try:
        user = auth.create_user_with_email_and_password(correo, password)  # ¡Firebase maneja la seguridad!
        
        datos_usuario = {
            "nombre": nombre,
            "apellido1": apellido1,
            "apellido2": apellido2,
            "fecha_nacimiento": fecha_nacimiento,
            "correo": correo,
            "licencia": licencia,
            "uid": user["localId"]  
        }
        
        db.child("usuarios").child(correo.replace(".", ",")).set(datos_usuario)
        print("Usuario registrado correctamente.")
        return True

    except Exception as e:
        print(f"Error al registrar usuario: {str(e)}")
        return False


def iniciar_sesion(correo, password):
    try:
        user = auth.sign_in_with_email_and_password(correo, password)
        uid = user["localId"]
        
        datos_usuario = db.child("usuarios").child(correo.replace(".", ",")).get().val()
        
        if datos_usuario:
            print("Inicio de sesión exitoso.")
            return datos_usuario  
        else:
            print("No se encontraron datos del usuario.")
            return None

    except Exception as e:
        print(f"Error en el inicio de sesión: {str(e)}")
        return None



class Personas:
    def __init__(self):
        self.db = db

    def lista_personas(self):
        try:
            datos = self.db.child("personas").get()
            print("Datos crudos desde Firebase:", datos.val())  
            return datos.val() if datos.val() else {}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {}
    
    def agregar_persona(self, nombre, edad):
        try:
            persona = {
                "nombre": nombre,
                "edad": edad
            }
            self.db.child("personas").push(persona)
            return True
        except Exception as e:
            print(f"Error al agregar persona: {str(e)}")
            return False

    def lista_pacientes(self):
        
        try:
            datos = self.db.child("pacientes").get()
            print("Datos de pacientes:", datos.val())  
            return datos.val() if datos.val() else {}
        except Exception as e:
            print(f"Error al listar pacientes: {str(e)}")
            return {}
    
    def agregar_paciente(self, datos_paciente):
        """Método para agregar un paciente completo con todos sus datos"""
        try:
            resultado = self.db.child("pacientes").push(datos_paciente)
            return True
        except Exception as e:
            print(f"Error al agregar paciente: {str(e)}")
            return False

    def obtener_usuario(self, usuario_id):
        try:
            usuario = self.db.child("usuarios").child(usuario_id).get().val()
            return usuario
        except Exception as e:
            print(f"Error al obtener usuario: {str(e)}")
            return None
