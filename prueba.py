import mysql.connector

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",       # Cambia si tu servidor MySQL está en otro host
    user="root",      # Tu usuario de MySQL
    password="", # Tu contraseña de MySQL
    database="escuela" # Nombre de tu base de datos
)

cursor = conexion.cursor()

# Consulta SELECT
consulta = "SELECT * FROM programas"
cursor.execute(consulta)

# Obtener y mostrar los resultados
resultados = cursor.fetchall()
for value in resultados:
    print(value)

# Cierre de la conexión
cursor.close()
conexion.close()