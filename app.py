from flask import Flask, request, jsonify

app = Flask(__name__)  # Asignandole nombre a Flask

# Biblioteca de datos
libros = {
    1: {
        "id": 1,
        "titulo": "Cien años de soledad",
        "autor": "Gabriel García Márquez",
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
        "calificacion": 9.2
    },
    3: {
        "id": 3,
        "titulo": "El principito",
        "autor": "Antoine de Saint-Exupéry",
        "anio": 1943,
        "genero": "fábula",
        "disponible": False,
        "calificacion": 8.8
    }
}

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
def ingresartlibro():  # Función para integrar libros a la Biblioteca con ID manual
    datos = request.get_json()

    # Condición para detectar si faltan campos
    campos = ['id', 'titulo', 'autor', 'anio',
              'genero', 'calificacion', 'disponible']
    if any(campo not in datos for campo in campos):
        return jsonify({'error': 'Faltan campos de datos'}), 400

#     if not datos.get('id') or not datos.get('titulo') or \
#    not datos.get('autor') or not datos.get('anio') or \
#    not datos.get('genero') or not datos.get('disponible') or \
#    not datos.get('calificacion'):
#       return jsonify({'error': 'Faltan campos de datos'}), 400

    # Condición para detectar si el ID ya está en uso
    if datos['id'] in libros:
        return jsonify({'error': 'El ID ya está en uso'}), 409

    libro = {
        'id': datos['id'],
        'titulo': datos['titulo'],
        'autor': datos['autor'],
        'anio': datos['anio'],
        'genero': datos['genero'],
        'disponible': datos['disponible'],
        'calificacion': datos['calificacion']

    }

    libros[datos['id']] = libro
    return jsonify(libro), 201


# Método GET para obtener elementos de la ruta /libros
@app.route('/libros', methods=["GET"])
def obtener_libros():  # Función para obtener todos los libros de la Biblioteca
    return jsonify(list(libros.values())), 201


# Método GET para obtener elementos de la ruta /libros/<int:libro_id>
# <int:libro_id> Es la forma de leer como int el ID
@app.route('/libros/<int:libro_id>', methods=["GET"])
def obtener_libro(libro_id):  # Función para obtener un libro a partir de su ID
    libro = libros.get(libro_id)
    if not libro:
        return jsonify({'error': 'Libro no encontrado'}), 404

    return jsonify(libro), 201

# Método PUT para reemplazar POR COMPLETO los elementos en la ruta /libros/<int:libro_id>


@app.route('/libros/<int:libro_id>', methods=["PUT"])
# Función para reemplazar todos los elementos del ID
def reemplazar_libro(libro_id):
    if libro_id not in libros:
        return jsonify({'error': 'Libro no encontrado'}), 404

    datos = request.get_json()

    # Si el ID del JSON no coincide con el del HTML, no se ejecuta
    if 'id' in datos and datos['id'] != libro_id:
        return jsonify({'error': 'El ID del JSON no coincide con el de la solicitud HTML'}), 400

    # Condición para detectar si faltan campos
    campos = ['id', 'titulo', 'autor', 'anio',
              'genero', 'calificacion', 'disponible']
    if any(campo not in datos for campo in campos):
        return jsonify({'error': 'Faltan campos de datos'}), 400

    libros[libro_id] = {
        'id': datos['id'],
        'titulo': datos['titulo'],
        'autor': datos['autor'],
        'anio': datos['anio'],
        'genero': datos['genero'],
        'disponible': datos['disponible'],
        'calificacion': datos['calificacion']
    }
    return jsonify(libros[libro_id]), 201


# Método PATCH para reemplazar UNO o VARIOS ELEMENTOS en la ruta /libros/<int:libro_id>
@app.route('/libros/<int:libro_id>', methods=["PATCH"])
# Función para actualizar uno o varios datos mediante el ID
def actualizar_libro(libro_id):
    if libro_id not in libros:
        return jsonify({'error': 'Libro no encontrado'}), 404

    datos = request.get_json()

    # Si el ID del JSON no coincide con el del HTML, no se ejecuta
    if 'id' in datos and datos['id'] != libro_id:
        return jsonify({'error': 'El ID del JSON no coincide con el de la solicitud HTML'}), 400

    libro = libros[libro_id]

    if 'titulo' in datos:
        libro['titulo'] = datos['titulo']
    if 'autor' in datos:
        libro['autor'] = datos['autor']
    if 'anio' in datos:
        libro['anio'] = datos['anio']
    if 'genero' in datos:
        libro['genero'] = datos['genero']
    if 'disponible' in datos:
        libro['disponible'] = datos['disponible']
    if 'calificacion' in datos:
        libro['calificacion'] = datos['calificacion']

    return jsonify(libro), 201


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
