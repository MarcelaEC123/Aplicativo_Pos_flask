import mysql.connector

import mysql.connector

def conectar_bd():
    try:
        # Configurar los parámetros de conexión
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Coloca tu contraseña si la tienes configurada
            database="Aplicativo_pos_final"
        )
        # Devolver la conexión y un cursor
        cursor = database.cursor()
        return database, cursor
    except mysql.connector.Error as error:
        raise RuntimeError("Error de conexión a la base de datos:", error)



def actualizar_producto(id_producto, codigo, descripcion, categoria, id_proveedor, nombre_proveedor, valor_unitario, unidad_medida, stock):
    try:
        db_connection, cursor = conectar_bd()
        if db_connection is None or cursor is None:
            return False
        sql = "UPDATE producto SET codigo = %s, descripcion = %s, categoria = %s, id_proveedor = %s, nombre_proveedor = %s, valor_unitario = %s, unidad_medida = %s, stock = %s WHERE id_producto = %s"
        data = (codigo, descripcion, categoria, id_proveedor, nombre_proveedor, valor_unitario, unidad_medida, stock, id_producto)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return True
    except mysql.connector.Error as error:
        print("Error al actualizar producto:", error)
        return False
    
def actualizar_usuario(id_usuario, nombre, tipo_Identificacion, numero_identificacion, telefono, email, usuario, contrasenia, tipo_usuario):
    try:
        db_connection, cursor = conectar_bd()
        if db_connection is None or cursor is None:
            return False
        sql = "UPDATE usuarios SET nombre = %s, tipo_identificacion = %s, numero_identificacion = %s, telefono = %s, email = %s, usuario = %s, contrasenia = %s, tipo_usuario = %s WHERE id_usuario = %s"
        data = (nombre, tipo_Identificacion, numero_identificacion, telefono, email, usuario, contrasenia, tipo_usuario, id_usuario)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return True
    except mysql.connector.Error as error:
        print("Error al actualizar usuario:", error)
        return False


def guardar_detalles_venta(codigo, descripcion, cantidad, valor_unitario, id_venta, id_producto):
    try:
        db_connection, cursor = conectar_bd()
        if db_connection is None or cursor is None:
            return False
        sql = "INSERT INTO detalle_venta (codigo, descripcion, cantidad, valor_unitario, id_venta, id_producto) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (codigo, descripcion, cantidad, valor_unitario, id_venta, id_producto)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return True
    except mysql.connector.Error as error:
        print("Error al guardar detalles de venta:", error)
        return False
    
def obtener_informacion_desde_bd(codigo_producto):
    try:
        db_connection, cursor = conectar_bd()
        if db_connection is None or cursor is None:
            return None

        sql = "SELECT descripcion, valor_unitario FROM producto WHERE codigo = %s"
        print("Consulta SQL:", sql)  # Imprimir la consulta SQL para depuración
        cursor.execute(sql, (codigo_producto,))
        producto_data = cursor.fetchone()
        cursor.close()
        db_connection.close()

        print("Datos del producto obtenidos:", producto_data)  # Imprimir los datos obtenidos para depuración
        return producto_data
    except mysql.connector.Error as error:
        print("Error al obtener información del producto desde la base de datos:", error)
        return None
