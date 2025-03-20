# app.py
import web
import os

# Asegurarse de que exista el directorio de sesiones
if not os.path.exists('sessions'):
    os.makedirs('sessions')

# Importar controladores
from controllers.iniciosesion import Iniciosesion as Iniciosesion
from controllers.admin_cedulas import AdminCedulas


# Definir URLs
urls = (
    '/', 'Index',
    '/iniciosesion', 'Iniciosesion',
    '/listapersonas', 'ListaPersonas',
    '/admin/cedulas', 'AdminCedulas',
    '/cerrar_sesion', 'CerrarSesion',
    '/acceso_denegado', 'AccesoDenegado',
    # Otras rutas...
)

app = web.application(urls, globals())

# Configurar sesión
if web.config.get('_session') is None:
    session = web.session.Session(
        app, 
        web.session.DiskStore('sessions'),
        initializer={
            'usuario': None, 
            'cedula_verificada': False,
            'mensaje': None
        }
    )
    web.config._session = session
else:
    session = web.config._session

# Hacer que la sesión esté disponible en los controladores
def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))

# Controlador para cerrar sesión
class CerrarSesion:
    def GET(self):
        session = web.ctx.session
        session.kill()
        raise web.seeother('/iniciosesion')

# Controlador para acceso denegado
class AccesoDenegado:
    def GET(self):
        return web.template.render("views/").acceso_denegado()

# Middleware para verificar autenticación (usar como decorador)
def requiere_login(func):
    def wrapper(self, *args, **kwargs):
        if not web.ctx.session.get('usuario'):
            # Guardar mensaje para mostrar después de iniciar sesión
            web.ctx.session.mensaje = "Debe iniciar sesión para acceder a esta página"
            raise web.seeother('/iniciosesion')
            
        # Verificar si la cédula ha sido verificada
        if not web.ctx.session.get('cedula_verificada'):
            web.ctx.session.mensaje = "Su cédula profesional debe ser verificada primero"
            raise web.seeother('/iniciosesion')
            
        return func(self, *args, **kwargs)
    return wrapper

# Middleware para verificar si es administrador
def requiere_admin(func):
    def wrapper(self, *args, **kwargs):
        if not web.ctx.session.get('usuario'):
            web.ctx.session.mensaje = "Debe iniciar sesión para acceder a esta página"
            raise web.seeother('/iniciosesion')
            
        usuario = web.ctx.session.get('usuario')
        if not usuario.get('es_admin', False):
            raise web.seeother('/acceso_denegado')
            
        return func(self, *args, **kwargs)
    return wrapper

# Ejemplo de cómo aplicar el decorador a tus controladores existentes:
"""
class ListaPersonas:
    @requiere_login
    def GET(self):
        # Código existente...
        pass
"""

if __name__ == "__main__":
    app.run()