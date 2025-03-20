# controllers/iniciosesion.py
import web
from models.pediatras import iniciar_sesion, db
from models.verificacion import verificar_cedula_profesional, verificar_cedula_local

render = web.template.render("views/")

class Iniciosesion:
    def GET(self):
        return render.iniciosesion(datos={})
        
    def POST(self):
        try:
            datos = web.input()
            correo = datos.correo
            password = datos.password
            
            print(f"Intentando iniciar sesión con: {correo}")
            usuario = iniciar_sesion(correo, password)
            print(f"Resultado de iniciar_sesion: {usuario}")
            
            if usuario:
                # Verificar la cédula profesional antes de permitir el acceso
                licencia = usuario.get("licencia", "")
                
                # Verifica si la cédula ya fue validada anteriormente
                usuario_id = correo.replace(".", ",")
                usuario_data = db.child("usuarios").child(usuario_id).get().val()
                
                if usuario_data and usuario_data.get("cedula_verificada", False):
                    # Cédula ya verificada previamente
                    session = web.ctx.session
                    session.usuario = usuario
                    session.cedula_verificada = True
                    print("✅ Sesión iniciada - cédula previamente verificada.")
                    return web.seeother("/listapersonas")
                
                # Si no está verificada, verificarla ahora
                # Opción 1: Verificar con API externa (puede ser lenta)
                # resultado_verificacion = verificar_cedula_profesional(licencia)
                
                # Opción 2: Verificar con base de datos local (más rápida)
                resultado_verificacion = verificar_cedula_local(licencia, db)
                
                if resultado_verificacion and resultado_verificacion.get("valida", False):
                    # Cédula verificada correctamente
                    session = web.ctx.session
                    session.usuario = usuario
                    session.cedula_verificada = True
                    
                    # Actualizar en la base de datos que ya fue verificada
                    db.child("usuarios").child(usuario_id).update({"cedula_verificada": True})
                    
                    print("✅ Sesión iniciada correctamente con cédula verificada.")
                    return web.seeother("/listapersonas")
                else:
                    # Cédula no válida
                    mensaje_error = resultado_verificacion.get("mensaje", "Cédula profesional no verificada")
                    print(f"❌ {mensaje_error}")
                    return render.iniciosesion(datos={"error": mensaje_error})
            else:
                print("❌ Credenciales incorrectas")
                return render.iniciosesion(datos={"error": "Correo o contraseña incorrectos."})
                
        except Exception as e:
            print(f"⚠️ Error en inicio de sesión: {str(e)}")
            return render.iniciosesion(datos={"error": str(e)})