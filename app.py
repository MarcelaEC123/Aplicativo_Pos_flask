import MySQLdb
from flask import Flask, request, render_template, redirect, url_for

 # Importa el modelo de Venta definido en tu aplicación

import database as db

app = Flask(__name__, template_folder="C:\\Users\\cindy\\OneDrive\\Escritorio\\Pagina_web\\templates")

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        db_connection, cursor = db.conectar_bd()
        query = "SELECT * FROM usuario WHERE Usuario = %s AND Contrasenia = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        db_connection.close()
        if user:
            return redirect(url_for("principal"))
        else:
            error_message = "Credenciales incorrectas"
            return render_template("mensaje.html", message=error_message)

    except Exception as e:
        error_message = "Error al procesar la solicitud: {}".format(str(e))
        return render_template("mensaje.html", message=error_message)
# Ruta para la página principal
@app.route("/principal")
def principal():
    return render_template("principal.html")

# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    return redirect(url_for("index"))


@app.route("/caja")
def caja():
    try:
        db_connection, cursor = db.conectar_bd()
        cursor.execute("SHOW TABLE STATUS LIKE 'venta'")
        table_status = cursor.fetchone()
        if table_status is not None:
            next_id = table_status[10]
            cursor.execute("SELECT COUNT(*) FROM venta")
            count = cursor.fetchone()[0]
            if count == 0:
                next_id = 1
            else:
                cursor.execute("SELECT MAX(id_venta) FROM venta")
                last_id = cursor.fetchone()[0]
                next_id = last_id + 1
            cursor.execute("SELECT MAX(id_factura) FROM venta")
            last_code = cursor.fetchone()[0]
            if last_code is not None:
                new_code = str(int(last_code) + 1).zfill(7)
            else:
                new_code = "0000001"
            cursor.execute("SELECT * FROM venta")
            myresult = cursor.fetchall()
            insertObjects = []
            columnNames = [column[0] for column in cursor.description]
            for record in myresult:
                insertObjects.append(dict(zip(columnNames, record)))
            cursor.close()
            return render_template("caja.html", data=insertObjects, next_id=next_id, new_code=new_code)
        else:
            return "No se pudo obtener información de la tabla 'venta'"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/guardarVenta', methods=['POST'])
def addGuardarVenta():
    # Obtener los datos del formulario de venta
    id_venta = request.form['id_venta']
    id_factura = request.form['id_factura']
    cliente_id_cliente = request.form['cliente_id_cliente']
    medio_pago = request.form['medio_pago']
    descuento = request.form['descuento']
    iva = request.form['iva']
    fecha_registro = request.form['fecha_registro']
    observaciones = request.form['observaciones']
    total_a_pagar = request.form['total_a_pagar']

    # Verificar que todos los campos necesarios estén presentes
    if id_venta and id_factura and cliente_id_cliente and medio_pago and descuento and iva and fecha_registro and observaciones and total_a_pagar:
        try:
            # Conectar a la base de datos
            db_connection, cursor = db.conectar_bd()

            # Insertar los datos en la tabla 'venta'
            sql_venta = "INSERT INTO venta (id_venta, id_factura, cliente_id_cliente, medio_pago, descuento, iva, fecha_registro, observaciones, total_a_pagar) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data_venta = (id_venta, id_factura, cliente_id_cliente, medio_pago, descuento, iva, fecha_registro, observaciones, total_a_pagar)
            cursor.execute(sql_venta, data_venta)

            # Obtener el ID de la venta recién insertada
            venta_id = cursor.lastrowid

            # Obtener los detalles de la venta del formulario
            detalles_venta = request.form.getlist('detalle_venta')

            # Insertar los detalles de la venta en la tabla 'detalle_venta'
            for detalle in detalles_venta:
                descripcion, cantidad, valor_unitario, id_producto = detalle.split(',')
                sql_detalle_venta = "INSERT INTO detalle_venta (descripcion, cantidad, valor_unitario, id_venta, id_producto) VALUES (%s, %s, %s, %s, %s)"
                data_detalle_venta = (descripcion, cantidad, valor_unitario, venta_id, id_producto)
                cursor.execute(sql_detalle_venta, data_detalle_venta)

            # Confirmar los cambios en la base de datos
            db_connection.commit()

            # Cerrar la conexión
            cursor.close()
            db_connection.close()

            # Redirigir a la página de caja
            return redirect(url_for('caja'))
        except Exception as e:
            # Manejar errores
            return f"Error al guardar la venta: {str(e)}"
    else:
        # Si no se proporcionaron todos los campos necesarios
        return "Por favor, complete todos los campos."

@app.route('/deleteVenta/<string:id_venta>')
def deleteVenta(id_venta):
    try:
        db_connection, cursor = db.conectar_bd()
        sql = "DELETE FROM venta WHERE id_venta = %s"
        cursor.execute(sql, (id_venta,))
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return redirect(url_for('caja'))
    except Exception as e:
        print("Error al eliminar la venta:", e)
        db_connection.rollback()
        cursor.close()
        db_connection.close()
        return "Error al eliminar la venta. Por favor, inténtalo de nuevo más tarde."


@app.route("/generar_ticket/<int:id_venta>")
def generar_ticket(id_venta):
    try:
        db_connection, cursor = db.conectar_bd()
        if db_connection is None:
            return "Error: No se pudo conectar a la base de datos"
        
        cursor.execute("SELECT dv.cantidad, dv.descripcion, dv.valor_unitario, v.id_factura, v.fecha_registro, v.total_a_pagar FROM detalle_venta dv INNER JOIN venta v ON dv.id_venta = v.id_venta WHERE dv.id_venta = %s", (id_venta,))
        venta_data = cursor.fetchall()
        
        if not venta_data:
            return "Error: No se encontraron datos para la venta especificada"
        
        cursor.close()
        db_connection.close()
        print("Datos de venta:", venta_data)
        return render_template("factura.html", venta=venta_data)
    except Exception as e:
        return f"Error al generar el ticket: {str(e)}"

def obtener_venta():
    # Aquí iría tu lógica para obtener los detalles de la venta
    # Por ahora, simplemente devolveré un diccionario ficticio con datos de ejemplo
    return {
        'id': 1,
        'id_factura': 'FAC001',
        'medio_pago': 'Efectivo',
        'descuento': 10,
        'iva': 5,
        'fecha_registro': '2024-04-15',
        'total_a_pagar': 100,
        'id_cliente': 123
    }

@app.route('/detalle_venta.html')
def detalle_venta():
    venta = obtener_venta()  # Reemplaza esto con tu lógica para obtener los detalles de la venta
    return render_template('detalle_venta.html', venta=venta)
# Definir el endpoint para guardar los detalles de la venta



@app.route("/clientes")
def clientes():
    db_connection, cursor = db.conectar_bd()
    
    # Obtener el próximo valor autoincremental de id_producto
    cursor.execute("SHOW TABLE STATUS LIKE 'cliente'")
    table_status = cursor.fetchone()
    next_id = table_status[10]  # El índice 10 corresponde a la columna Auto_increment
    
    # Contar la cantidad de registros
    cursor.execute("SELECT COUNT(*) FROM cliente")
    count = cursor.fetchone()[0]
    if count == 0:
        next_id = 1  # Si no hay registros, comenzar desde 1
    else:
        # Obtener el último ID y ajustar para el siguiente ID
        cursor.execute("SELECT MAX(id_cliente) FROM cliente")
        last_id = cursor.fetchone()[0]
        next_id = last_id + 1
    
    # Obtener los productos existentes
    cursor.execute("SELECT * FROM cliente")
    myresult = cursor.fetchall()
    # Convertir datos a diccionario
    insertObjec = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObjec.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template("clientes.html", data=insertObjec, next_id=next_id)


#Ruta para guardar CLIENTES
@app.route('/guardarClientes', methods=['POST'])
def addGuardarClientes():    
     id_cliente = request.form['id_cliente']
     tipo_identificacion = request.form['tipo_identificacion']
     numero_identificacion = request.form['numero_identificacion']
     nombre_completo = request.form['nombre_completo']
     email = request.form['email']
     direccion = request.form['direccion']
     telefono = request.form['telefono']
    
     if id_cliente and tipo_identificacion and numero_identificacion and nombre_completo and  email and direccion and  telefono :
        db_connection, cursor = db.conectar_bd()
        sql = "INSERT INTO cliente (id_cliente,tipo_identificacion,numero_identificacion,nombre_completo, email,direccion, telefono) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        data = (id_cliente,tipo_identificacion,numero_identificacion,nombre_completo,email,direccion,telefono)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
     return redirect(url_for('clientes'))

@app.route('/deleteCliente/<string:id_cliente>')
def deleteCliente (id_cliente):
        db_connection, cursor = db.conectar_bd()
        sql = "DELETE FROM cliente WHERE id_cliente=%s"
        data = (id_cliente,)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return redirect(url_for('clientes'))

@app.route("/proveedores")
def proveedores():
    db_connection, cursor = db.conectar_bd()
    
       # Obtener el próximo valor autoincremental de id_producto
    cursor.execute("SHOW TABLE STATUS LIKE 'proveedor'")
    table_status = cursor.fetchone()
    next_id = table_status[10]  # El índice 10 corresponde a la columna Auto_increment
    
    # Contar la cantidad de registros
    cursor.execute("SELECT COUNT(*) FROM proveedor")
    count = cursor.fetchone()[0]
    if count == 0:
        next_id = 1  # Si no hay registros, comenzar desde 1
    else:
        # Obtener el último ID y ajustar para el siguiente ID
        cursor.execute("SELECT MAX(id_proveedor) FROM proveedor")
        last_id = cursor.fetchone()[0]
        next_id = last_id + 1
    
    # Obtener los productos existentes
    cursor.execute("SELECT * FROM proveedor")
    myresult = cursor.fetchall()
    # Convertir datos a diccionario
    insertObjec = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObjec.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template("proveedores.html", data=insertObjec, next_id=next_id)

#Ruta para guardar PROVEEDORES
@app.route('/guardarProveedores', methods=['POST'])
def addGuardarPreveedores():    
     id_proveedor = request.form['id_proveedor']
     tipo_identificacion = request.form['tipo_identificacion']
     numero_identificacion = request.form['numero_identificacion']
     nombre_proveedor = request.form['nombre_proveedor']
     email = request.form['email']
     direccion = request.form['direccion']
     telefono = request.form['telefono']
     dia_de_visita = request.form['dia_de_visita']
     dia_de_entrega = request.form['dia_de_entrega']
    
     if id_proveedor and tipo_identificacion and numero_identificacion and nombre_proveedor  and  email and direccion and  telefono and dia_de_visita and dia_de_entrega:
        db_connection, cursor = db.conectar_bd()
        sql = "INSERT INTO proveedor (id_proveedor,tipo_identificacion,numero_identificacion, nombre_proveedor , email,direccion, telefono , dia_de_visita, dia_de_entrega) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        data = (id_proveedor,tipo_identificacion,numero_identificacion, nombre_proveedor ,email,direccion,telefono,dia_de_visita,dia_de_entrega)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
     return redirect(url_for('proveedores'))

@app.route('/deleteProveedor/<string:id_proveedor>')
def deleteProveedor (id_proveedor):
        db_connection, cursor = db.conectar_bd()
        sql = "DELETE FROM proveedor WHERE id_proveedor=%s"
        data = (id_proveedor,)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return redirect(url_for('proveedores'))

@app.route('/editar_proveedor', methods=['POST'])
def editar_proveedor():
    # Tu lógica para editar el proveedor aquí

    if request.method == 'POST':
        id_proveedor = request.form['id_proveedor']
        tipo_identificacion = request.form['tipo_identificacion']
        numero_identificacion = request.form['numero_identificacion']
        nombre_proveedor = request.form['nombre_proveedor']
        email = request.form['email']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        dia_de_visita = request.form['dia_de_visita']
        dia_de_entrega = request.form['dia_de_entrega']

        if id_proveedor and tipo_identificacion and numero_identificacion and nombre_proveedor and email and direccion and telefono and dia_de_visita and dia_de_entrega:
            if db.actualizar_proveedor(id_proveedor, tipo_identificacion, numero_identificacion, nombre_proveedor, email, direccion, telefono, dia_de_visita, dia_de_entrega):
                return 'Proveedor editado exitosamente'
            else:
                return 'Proveedor no encontrado'
        else:
            return 'Todos los campos son obligatorios'



#Ruta para guardar PRODUCTOS
@app.route("/productos")
def productos():
    db_connection, cursor = db.conectar_bd()
    
    # Obtener el próximo valor autoincremental de id_producto
    cursor.execute("SHOW TABLE STATUS LIKE 'producto'")
    table_status = cursor.fetchone()
    next_id = table_status[10]  # El índice 10 corresponde a la columna Auto_increment
    
    # Contar la cantidad de registros
    cursor.execute("SELECT COUNT(*) FROM producto")
    count = cursor.fetchone()[0]
    if count == 0:
        next_id = 1  # Si no hay registros, comenzar desde 1
    else:
        # Obtener el último ID y ajustar para el siguiente ID
        cursor.execute("SELECT MAX(id_producto) FROM producto")
        last_id = cursor.fetchone()[0]
        next_id = last_id + 1
    # Generar el nuevo código
    cursor.execute("SELECT MAX(codigo) FROM producto")
    last_code = cursor.fetchone()[0]
    if last_code:
        new_code = str(int(last_code) + 1).zfill(4)  # Incrementar el último código y rellenar con ceros
    else:
        new_code = "0001"  # Si no hay códigos en la base de datos, iniciar desde "0001"
    # Obtener los productos existentes
    cursor.execute("SELECT * FROM producto")
    myresult = cursor.fetchall()
    # Convertir datos a diccionario
    insertObjec = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObjec.append(dict(zip(columnNames, record)))
    cursor.close()
    return render_template("productos.html", data=insertObjec, next_id=next_id, new_code=new_code)

# Ruta para guardar productos
@app.route('/guardar', methods=['POST'])
def addGuardar():    
     codigo = request.form['codigo']
     descripcion = request.form['descripcion']
     categoria = request.form['categoria']
     nombre_proveedor = request.form['nombre_proveedor']
     stock = request.form['stock']
     valorUnitario = request.form['valor_unitario']
     unidadMedida = request.form['unidad_medida']

     if codigo and descripcion and categoria and nombre_proveedor and stock and valorUnitario and unidadMedida:
        db_connection, cursor = db.conectar_bd()
        sql = "INSERT INTO producto (codigo,descripcion,categoria,nombre_proveedor,stock,valor_unitario,unidad_medida) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        data = (codigo,descripcion,categoria,nombre_proveedor,stock,valorUnitario,unidadMedida)
        cursor.execute(sql, data)
        db_connection.commit()
    
        cursor.close()
        db_connection.close()
    
     return redirect(url_for('productos'))

# Ruta para agregar stock
@app.route('/addStock', methods=['POST'])
def addStock():
    id_producto = request.form['id_producto']
    cantidad = request.form['cantidad']

    if id_producto and cantidad:
        db_connection, cursor = db.conectar_bd()
        # Obtener el stock actual del producto
        cursor.execute("SELECT stock FROM producto WHERE id_producto = %s", (id_producto,))
        stock_actual = cursor.fetchone()[0]

        # Sumar la cantidad proporcionada al stock actual
        nuevo_stock = stock_actual + int(cantidad)

        # Actualizar el stock en la base de datos
        cursor.execute("UPDATE producto SET stock = %s WHERE id_producto = %s", (nuevo_stock, id_producto))  # Corregido aquí
        db_connection.commit()

        cursor.close()
        db_connection.close()

    return redirect(url_for('productos'))


@app.route('/deleteProducto/<string:id_producto>')
def delete (id_producto):
        db_connection, cursor = db.conectar_bd()
        sql = "DELETE FROM producto WHERE id_producto=%s"
        data = (id_producto,)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return redirect(url_for('productos'))

@app.route('/editar_producto', methods=['POST'])
def editar_producto():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        codigo = request.form['codigo']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        id_proveedor = request.form['id_proveedor']
        nombre_proveedor = request.form['nombre_proveedor']
        valor_unitario = request.form['valor_unitario']
        unidad_medida = request.form['unidad_medida']
        stock = request.form['stock']

        if id_producto and codigo and descripcion and categoria and id_proveedor and nombre_proveedor and valor_unitario and unidad_medida and stock:
            if db.actualizar_producto(id_producto, codigo, descripcion, categoria, id_proveedor, nombre_proveedor, valor_unitario, unidad_medida, stock):
                return 'Producto editado exitosamente', 200
            else:
                return 'Producto no encontrado', 404
        else:
            return 'Todos los campos son obligatorios', 400


# Ruta para mostrar usuarios
@app.route("/usuarios")
def usuarios():
    db_connection, cursor = db.conectar_bd()
    
    # Obtener el último ID insertado antes de eliminar registros
    cursor.execute("SELECT MAX(id_usuario) FROM usuario")
    last_id = cursor.fetchone()[0]

    # Calcular el próximo ID
    if last_id is None:
        next_id = 1
    else:
        next_id = last_id + 1
    
    # Obtener los usuarios existentes
    cursor.execute("SELECT * FROM usuario")
    myresult = cursor.fetchall()
    
    # Convertir datos a diccionario
    insertObjec = []
    columnNames = [column[0] for column in cursor.description]
    for record in myresult:
        insertObjec.append(dict(zip(columnNames, record)))
    
    cursor.close()
    
    return render_template("usuarios.html", data=insertObjec, next_id=next_id)

# Ruta para guardar usuarios
@app.route('/guardarUsuario', methods=['POST'])
def addGuardarUsuario():    
    nombre = request.form['nombre']
    tipo_Identificacion = request.form['tipo_identificacion']
    numero_identificacion = request.form['numero_identificacion']
    telefono = request.form['telefono']
    email = request.form['email']
    usuario = request.form['usuario']
    contrasenia = request.form['contrasenia']
    tipo_usuario = request.form['tipo_usuario']

    if nombre and tipo_Identificacion and numero_identificacion and telefono and email and usuario and contrasenia and tipo_usuario:
        # Conectar a la base de datos
        db_connection, cursor = db.conectar_bd()

        # Obtener el último ID insertado antes de eliminar registros
        cursor.execute("SELECT MAX(id_usuario) FROM usuario")
        last_id = cursor.fetchone()[0]

        # Calcular el próximo ID
        if last_id is None:
            next_id = 1
        else:
            next_id = last_id + 1

        # Insertar el nuevo usuario en la tabla usuarios
        sql = "INSERT INTO usuario(id_usuario, nombre, tipo_Identificacion, numero_identificacion, telefono, email, usuario, contrasenia, tipo_usuario) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (next_id, nombre, tipo_Identificacion, numero_identificacion, telefono, email, usuario, contrasenia, tipo_usuario)
        cursor.execute(sql, data)
        db_connection.commit()

        # Cerrar la conexión
        cursor.close()
        db_connection.close()

    return redirect(url_for('usuarios'))

@app.route('/deleteUsuarios/<string:id_usuario>')
def deleteUsuarios(id_usuario):
        db_connection, cursor = db.conectar_bd()
        sql = "DELETE FROM usuario WHERE id_usuario=%s"
        data = (id_usuario,)
        cursor.execute(sql, data)
        db_connection.commit()
        cursor.close()
        db_connection.close()
        return redirect(url_for('usuarios'))


@app.route('/editar_usuario', methods=['POST'])
def editar_usuario():
    # Tu lógica para editar el proveedor aquí

    if request.method == 'POST':
        id_usuario = request.form['id_usuario']
        nombre = request.form['nombre']
        tipo_Identificacion = request.form['tipo_identificacion']
        numero_identificacion = request.form['numero_identificacion']
        telefono = request.form['telefono']
        email = request.form['email']
        usuario = request.form['usuario']
        contrasenia = request.form['contrasenia']
        tipo_usuario = request.form['tipo_usuario']

        if nombre and tipo_Identificacion and numero_identificacion and telefono and email and usuario and contrasenia and tipo_usuario:
            if db.actualizar_usuario(id_usuario, nombre, tipo_Identificacion, numero_identificacion, telefono, email, usuario, contrasenia, tipo_usuario):
                return 'Usuario editado exitosamente'
            else:
                return 'Usuario no encontrado'
        else:
            return 'Todos los campos son obligatorios'

if __name__ == "__main__":
    app.run(debug=True)


