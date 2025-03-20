# models/verificacion.py
import web
import requests
import json
import re
from bs4 import BeautifulSoup

def verificar_cedula_profesional(cedula):
    """
    Verifica si una cédula profesional es válida utilizando web scraping
    a la página del Registro Nacional de Profesionistas.
    
    Args:
        cedula (str): Número de cédula profesional a verificar
        
    Returns:
        dict: Información del profesionista si es válida, None si no es válida
    """
    try:
        # Validación básica del formato de la cédula (solo números y longitud adecuada)
        if not re.match(r'^\d{7,8}$', cedula):
            return {"valida": False, "mensaje": "Formato de cédula inválido"}
            
        # URL del servicio de consulta (esto puede cambiar en el futuro)
        url = "https://www.cedulaprofesional.sep.gob.mx/cedula/buscaCedulaJson.action"
        
        # Datos para la solicitud POST
        datos = {
            "json": json.dumps({
                "maxResult": "1000",
                "nombre": "",
                "paterno": "",
                "materno": "",
                "idCedula": cedula
            })
        }
        
        # Realizar la solicitud
        response = requests.post(url, data=datos)
        
        # Verificar respuesta
        if response.status_code == 200:
            respuesta = response.json()
            if respuesta and "items" in respuesta and respuesta["items"]:
                # La cédula existe, extraer información
                info_cedula = respuesta["items"][0]
                return {
                    "valida": True,
                    "nombre": info_cedula.get("nombre", ""),
                    "apellido_paterno": info_cedula.get("paterno", ""),
                    "apellido_materno": info_cedula.get("materno", ""),
                    "numero_cedula": info_cedula.get("idCedula", ""),
                    "institucion": info_cedula.get("institucion", ""),
                    "carrera": info_cedula.get("carrera", "")
                }
            else:
                # No se encontró la cédula
                return {
                    "valida": False,
                    "mensaje": "Cédula profesional no encontrada en el registro"
                }
        else:
            # Error en la solicitud
            return {
                "valida": False,
                "mensaje": f"Error al consultar el servicio: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "valida": False,
            "mensaje": f"Error en la verificación: {str(e)}"
        }

def verificar_cedula_local(cedula, db):
    """
    Verifica una cédula profesional contra una base de datos local en Firebase
    
    Args:
        cedula (str): Número de cédula a verificar
        db: Referencia a la base de datos de Firebase
        
    Returns:
        dict: Información si la cédula es válida, None si no lo es
    """
    try:
        # Buscar la cédula en la base de datos
        resultado = db.child("cedulas_validas").child(cedula).get().val()
        if resultado:
            return {
                "valida": True,
                "datos": resultado
            }
        else:
            return {
                "valida": False,
                "mensaje": "Cédula no encontrada en la base de datos"
            }
    except Exception as e:
        return {
            "valida": False, 
            "mensaje": f"Error al verificar la cédula: {str(e)}"
        }