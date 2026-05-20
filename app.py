from flask import Flask, request, jsonify

app = Flask(__name__)  # Asignandole nombre a Flask

# Biblioteca de datos
libros = {
    1: {
        "id": 1,
        "titulo": "Cien años de soledad",
        "autor": "George Orwell",
        "anio": 1967,
        "genero": "realismo mágico",
        "disponible": True,
        "calificacion": 9.5
    },
    2: {
        "id": 2,
        "titulo": "1984",
        "autor": "George Orwell",
        "anio": 1949,
        "genero": "distopía",
        "disponible": True,
        "calificacion": 10
    },
    3: {
        "id": 3,
        "titulo": "El principito",
        "autor": "Antoine de Saint-Exupéry",
        "anio": 1943,
        "genero": "fábula",
        "disponible": False,
        "calificacion": 10
    }
}

contador_id = 4  # Empieza en 4 porque ya hay 3 libros

# CÓDIGOS HTTP
# 200 - Solicitud exitosa
# 201 - Se ha creado un nuevo elemento
# 400 - La sintáxis en inválida o incompleta
# 404 - Elemento no encontrado
# 409 - La acción no puede ejecutarse

# Referencia de ruta o también conocido como ENDPOINT (sin método)


@app.route("/")
def root():  # Función para regresar el mensaje "Bienvenido"
    return "Bienvenido a la biblioteca", 200


# Método POST para integrar elementos dentro de la ruta /libros
@app.route('/libros', methods=["POST"])
def ingresar_libro():  # Función para integrar libros a la Biblioteca con ID manual
    global contador_id
    datos = request.get_json()

    if isinstance(datos, dict):
        datos = [datos]

    if not isinstance(datos, list):
        return jsonify({'error': 'Se esperaba un objeto o lista de libros'}), 400

    campos_base = ['titulo', 'autor', 'anio',
                   'genero', 'calificacion', 'disponible']
    campos_protegidos = {'id'}
    guardados = []
    errores = []

    for i, libro_datos in enumerate(datos):
        if any(campo not in libro_datos for campo in campos_base):
            errores.append({'libro': i + 1, 'error': 'Faltan campos de datos'})
            continue

        # Campos base obligatorios
        libro = {
            'id': contador_id,
            'titulo': libro_datos['titulo'],
            'autor': libro_datos['autor'],
            'anio': libro_datos['anio'],
            'genero': libro_datos['genero'],
            'disponible': libro_datos['disponible'],
            'calificacion': libro_datos['calificacion']
        }

        # Campos extra — cualquier campo adicional que no sea base ni id
        for campo, valor in libro_datos.items():
            if campo not in campos_base and campo not in campos_protegidos:
                libro[campo] = valor

        libros[contador_id] = libro
        guardados.append(libro)
        contador_id += 1

    return jsonify({'guardados': guardados, 'errores': errores}), 201


# Método GET para obtener elementos de la ruta /libros/<int:libro_id>

@app.route('/libros', methods=["GET"])
def obtener_libros():
    datos = list(libros.values())

    autor = request.args.get('autor')
    if autor:
        datos = [valor for valor in datos if autor.lower()
                 in valor['autor'].lower()]

    genero = request.args.get('genero')
    if genero:
        datos = [valor for valor in datos if genero.lower()
                 in valor['genero'].lower()]

    disponibilidad = request.args.get('disponible')
    if disponibilidad is not None:
        disponible = disponibilidad.lower() == 'true'
        datos = [
            valor for valor in datos if valor['disponible'] == disponible]

    # if disponibilidad is None:
    #     disponible = disponibilidad.lower() == 'false'
    #     datos = [
    #         valor for valor in datos if valor['disponible'] == disponible]

    calificacion = request.args.get('calificacion')

    # Para la calificacion que es un float, la forma de evaluar sin condicional es con try/except
    if calificacion:
        try:
            calificacion = float(calificacion)
        except ValueError:
            return jsonify({
                'error': 'La calificación debe ser un número'
            }), 400

        datos = [
            valor for valor in datos if valor['calificacion'] == float(calificacion)]

    anio = request.args.get('anio')
    if anio:
        if not anio.isdigit():
            return jsonify({'error': 'El año debe contener el número completo'}), 400
        datos = [
            valor for valor in datos if valor['anio'] == int(anio)]

    libro_id = request.args.get('id')
    if libro_id:
        if not libro_id.isdigit():
            return jsonify({'error': 'El ID debe ser un número'}), 400
        datos = [
            valor for valor in datos if valor['id'] == int(libro_id)]

    if not datos:
        return jsonify({'mensaje': 'No se encontraron libros con esos valores'}), 404

    return jsonify(datos), 200


# Método PUT para reemplazar POR COMPLETO los elementos en la ruta /libros/<int:libro_id>


@app.route('/libros/<int:libro_id>', methods=["PUT"])
# Función para reemplazar todos los elementos del ID
def reemplazar_libro(libro_id):
    if libro_id not in libros:
        return jsonify({'error': 'Libro no encontrado'}), 404

    datos = request.get_json()

    # Si el ID trata de ser modificado, no se ejecuta
    if 'id' in datos:
        return jsonify({'error': 'El ID no puede ser modificado'}), 400

    # Condición para detectar si faltan campos
    campos = ['titulo', 'autor', 'anio',
              'genero', 'calificacion', 'disponible']
    if any(campo not in datos for campo in campos):
        return jsonify({'error': 'Faltan campos de datos'}), 400

    libros[libro_id] = {
        'id': libro_id,
        'titulo': datos['titulo'],
        'autor': datos['autor'],
        'anio': datos['anio'],
        'genero': datos['genero'],
        'disponible': datos['disponible'],
        'calificacion': datos['calificacion']
    }
    return jsonify(libros[libro_id]), 201


# Método PATCH para reemplazar UNO o VARIOS ELEMENTOS en la ruta /libros/<int:libro_id>
# PATCH múltiple - modifica varios libros a la vez
# Cada elemento de la lista debe tener "id" para saber cuál modificar
# Ejemplo: PATCH /libros
@app.route('/libros', methods=["PATCH"])
def actualizar_libros():
    datos = request.get_json()

    if isinstance(datos, dict):
        datos = [datos]

    if not isinstance(datos, list):
        return jsonify({'error': 'Se esperaba un objeto o lista de libros'}), 400

    campos_protegidos = {'id'}
    actualizados = []
    errores = []

    for i, bloque in enumerate(datos):
        # Cada bloque necesita un ID para saber qué libro modificar
        if 'id' not in bloque:
            errores.append(
                {'elemento': i + 1, 'error': 'Falta el ID del libro a modificar'})
            continue

        libro_id = bloque['id']

        if libro_id not in libros:
            errores.append(
                {'elemento': i + 1, 'error': f'Libro con ID {libro_id} no encontrado'})
            continue

        libro = libros[libro_id]
        campos_actualizados = []

        for campo, valor in bloque.items():
            if campo not in campos_protegidos:
                libro[campo] = valor
                campos_actualizados.append(campo)

        actualizados.append({
            'id': libro_id,
            'campos_actualizados': campos_actualizados,
            'libro': libro
        })

    return jsonify({'actualizados': actualizados, 'errores': errores}), 200


# PATCH múltiple de campos - agrega campos nuevos a varios libros a la vez
# Ejemplo: PATCH /libros/campos

@app.route('/libros/campos', methods=["PATCH"])
def agregar_campos_varios():
    datos = request.get_json()

    if isinstance(datos, dict):
        datos = [datos]

    if not isinstance(datos, list):
        return jsonify({'error': 'Se esperaba un objeto o lista'}), 400

    campos_protegidos = {'id', 'titulo', 'autor',
                         'anio', 'genero', 'disponible', 'calificacion'}
    agregados = []
    errores = []

    for i, bloque in enumerate(datos):
        if 'id' not in bloque:
            errores.append(
                {'elemento': i + 1, 'error': 'Falta el ID del libro'})
            continue

        libro_id = bloque['id']

        if libro_id not in libros:
            errores.append(
                {'elemento': i + 1, 'error': f'Libro con ID {libro_id} no encontrado'})
            continue

        if 'campos' not in bloque:
            errores.append(
                {'elemento': i + 1, 'error': 'Falta la clave "campos"'})
            continue

        campos_agregados = []

        for entrada in bloque['campos']:
            if 'tipo' not in entrada or 'valor' not in entrada:
                errores.append(
                    {'elemento': i + 1, 'error': 'Cada campo debe tener "tipo" y "valor"'})
                continue

            if entrada['tipo'] in campos_protegidos:
                errores.append(
                    {'elemento': i + 1, 'error': f'"{entrada["tipo"]}" es un campo base'})
                continue

            libros[libro_id][entrada['tipo']] = entrada['valor']
            campos_agregados.append(entrada['tipo'])

        agregados.append({
            'id': libro_id,
            'campos_agregados': campos_agregados,
            'libro': libros[libro_id]
        })

    return jsonify({'agregados': agregados, 'errores': errores}), 201

# Método para BORRAR EL ELEMENTO en la ruta /libros/<int:libro_id>


@app.route('/libros/<int:libro_id>', methods=["DELETE"])
def eliminar_libro(libro_id):  # Función para eliminar el libro por su ID
    if libro_id not in libros:
        return jsonify({'error': 'Libro no encontrado'}), 404

    libro_eliminado = libros.pop(libro_id)
    return jsonify({'mensaje': 'El libro ha sido eliminado', 'libro': libro_eliminado}), 201


# Método para hacer que la aplicación se ejecute
if __name__ == "__main__":
    app.run(debug=True)
