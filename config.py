"""
Configuración central del proyecto.
Los nombres de la hoja de cálculo y de cada pestaña son constantes fijas,
igual que en el Excel original (una pestaña = un tipo de dato).
"""

# Nombre del archivo de Google Sheets (debe existir y estar compartido
# con el correo del service account, ver README para el paso a paso)
NOMBRE_SPREADSHEET = "Presupuesto"

# Nombres de las pestañas dentro del spreadsheet
HOJA_PROYECCION = "Proyeccion"   # equivalente a "Proyección y seguimiento"
HOJA_GASTOS = "Gastos"           # equivalente a "Registro de gastos"
HOJA_SERVICIOS = "Servicios"     # equivalente a "Cálculo de servicios"

# Columnas esperadas en cada pestaña
COLUMNAS_PROYECCION = ["Rubro", "Proyectado", "Gastado", "Disponible"]
COLUMNAS_GASTOS = ["Fecha", "Item", "Valor", "Categoria"]
COLUMNAS_SERVICIOS = ["Servicio", "Valor"]

# Palabras clave que identifican cada servicio dentro del Item de un gasto
# (igual que el arreglo "palabras" de la macro original)
PALABRAS_SERVICIOS = ["Plex", "Spoti", "Internet", "Agua", "Cel", "Luz", "Gas"]

# Nombre exacto del rubro/categoria "Servicios" en Proyeccion y en Gastos.
# Un gasto solo cuenta como pago de servicio si además de contener la
# palabra clave, está clasificado con esta categoria.
CATEGORIA_SERVICIOS = "Servicios"

# Ruta al archivo de credenciales del service account de Google Cloud
RUTA_CREDENCIALES = "credentials.json"
