# controllers/admin_cedulas.py
import web
import datetime
from models.pediatras import db

render = web.template.render("views/admin/")

class AdminCedulas:
    def __init__(self):
        # Verificar si el usuario está autenticado y es administrador
        if not hasattr(web.ctx, 'session') or not web.ctx.session.get('usuario'):
            raise web.seeother('/iniciosesion')
            
        # Verificar si el usuario es administrador
        usuario = web.ctx.session.usuario
        if not usuario.get('es_admin', False):
            # Redirigir si no es administrador
            raise web.seeother('/acceso_denegado')
    
    def GET(self):
        try:
            # Obtener todas las cédulas registradas
            cedulas = db.child("cedulas_validas").get().val() or {}
            return render.cedulas(cedulas=cedulas, mensaje="")
        except Exception as e:
            return render.cedulas(cedulas={}, mensaje=f"Error: {str(e)}")
    
    def POST(self):
        try:
            datos = web.input()
            accion = datos.get('accion', '')
            
            if accion == 'agregar':
                # Agregar nueva cédula
                numero_cedula = datos.get('numero_cedula', '')
                nombre = datos.get('nombre', '')
                especialidad = datos.get('especialidad', '')
                institucion = datos.get('institucion', '')
                
                if not numero_cedula:
                    return render.cedulas(cedulas=self.obtener_cedulas(), 
                                         mensaje="Error: El número de cédula es obligatorio")
                
                # Fecha actual en formato adecuado
                fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                datos_cedula = {
                    "nombre": nombre,
                    "especialidad": especialidad,
                    "institucion": institucion,
                    "fecha_registro": fecha_actual,
                    "registrado_por": web.ctx.session.usuario.get('correo', 'sistema')
                }
                
                db.child("cedulas_validas").child(numero_cedula).set(datos_cedula)
                return web.seeother('/admin/cedulas')
                
            elif accion == 'eliminar':
                # Eliminar cédula
                numero_cedula = datos.get('numero_cedula', '')
                if numero_cedula:
                    db.child("cedulas_validas").child(numero_cedula).remove()
                return web.seeother('/admin/cedulas')
                
            elif accion == 'buscar':
                # Implementar búsqueda en DB
                termino = datos.get('termino', '')
                if termino:
                    # En Firebase no hay búsqueda directa, hay que implementarla manualmente
                    cedulas = self.obtener_cedulas()
                    resultados = {}
                    
                    for cedula_id, cedula_info in cedulas.items():
                        # Buscar en número de cédula, nombre o institución
                        if (termino in cedula_id or 
                            termino.lower() in cedula_info.get('nombre', '').lower() or
                            termino.lower() in cedula_info.get('institucion', '').lower()):
                            resultados[cedula_id] = cedula_info
                            
                    return render.cedulas(cedulas=resultados, mensaje=f"Resultados para: {termino}")
                else:
                    return web.seeother('/admin/cedulas')
            else:
                return render.cedulas(cedulas=self.obtener_cedulas(), 
                                     mensaje="Acción no reconocida")
                
        except Exception as e:
            return render.cedulas(cedulas=self.obtener_cedulas(), 
                                 mensaje=f"Error: {str(e)}")
    
    def obtener_cedulas(self):
        try:
            return db.child("cedulas_validas").get().val() or {}
        except:
            return {}