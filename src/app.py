"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


"""Crea una API conectada a una base de datos e implemente los siguientes endpoints (muy similares a SWAPI.dev or SWAPI.tech):

[GET] /people Listar todos los registros de people en la base de datos."""
@app.route('/people', methods=['GET'])
def get_all_people():

    people = People.query.all()
    return jsonify([item.serialize() for item in people]), 200

    
"""[GET] /people/<int:people_id> Muestra la información de un solo personaje según su id."""

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)

    if person is None:
        return jsonify({"error": "Person not found"}), 404
    else:
        return jsonify(person.serialize()), 200


"[GET] /planets Listar todos los registros de planets en la base de datos."

@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()
    return jsonify([item.serialize() for item in all_planets]), 200


"[GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id."

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    one_planet = Planet.query.get(planet_id)

    if one_planet is None:
        return jsonify({"error": "Planet not found"}), 404
    else:
        return jsonify(one_planet.serialize()), 200

"""Adicionalmente, necesitamos crear los siguientes endpoints para que podamos tener usuarios y favoritos en nuestro blog:

[GET] /users Listar todos los usuarios del blog."""

@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    return jsonify([item.serialize() for item in all_users]), 200

"[GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual."

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites_user = Favorite.query.all()
    return jsonify([item.serializa() for item in favorites_user]), 200

""" [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id."""
   
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def post_favorite_planet(planet_id):
    body = request.json

    # Validar que el planeta exista
    planet_exist = Planet.query.get(planet_id)
    if not planet_exist:
        return jsonify({"error": "Planet not found"}), 404
    
    # Verificar si ya es favorito
    planet_existing_fav = Favorite.query.filter_by(user_id = body['user_id'], planet_id=planet_id).first()
    if planet_existing_fav:
        return jsonify({"message": "Planet already in favorites"}), 409
    
    # Crear nuevo favorito
    new_favorite_planet = Favorite(user_id = body['user_id'], planet_id=planet_id)
    db.session.add(new_favorite_planet)

    try:
        db.session.commit()
        return jsonify({"message": "Planet added to favorites"}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500


"[POST] /favorite/people/<int:people_id> Añade un nuevo people favorito al usuario actual con el id = people_id."

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def post_favorite_person(people_id):
    body = request.json

    # Validar que el personaje exista
    person_exist = People.query.get(people_id)
    if not person_exist:
        return jsonify({"error": "Person not found"}), 404
    
    # Verificar si ya es favorito
    person_existing_fav = Favorite.query.filter_by(user_id = body['user_id'], people_id = people_id).first()
    if person_existing_fav:
        return jsonify({"message": "Person already in favorites"}), 409
    
    # Crear nuevo favorito
    new_favorite_person = Favorite(user_id = body['user_id'], people_id = people_id)
    db.session.add(new_favorite_person)

    try:
        db.session.commit()
        return jsonify({"message": "Person added to favorites"}), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500

"[DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id."

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):

    # Verificar que el favorito exista.
    favorite = Favorite.query.filter_by(planet_id=planet_id).first()

    if not favorite:
        return jsonify({"error": "Favorite planet not found"}), 404

    # Eliminar favorito
    db.session.delete(favorite)

    try:
        db.session.commit()
        return jsonify({"message": "Planet removed from favorites"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500

"[DELETE] /favorite/people/<int:people_id> Elimina un people favorito con el id = people_id."

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):

    # Verificar que el favorito exista.
    favorite = Favorite.query.filter_by(people_id = people_id).first()

    if not favorite:
        return jsonify({"error": "Favorite people not found"}), 404

    # Eliminar favorito
    db.session.delete(favorite)

    try:
        db.session.commit()
        return jsonify({"message": "People removed from favorites"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)






# OTROS CODIGOS VISTOS EN CLASE:

# 1) PARA PEOPLE:

@app.route("/planet-population",  methods=["GET"])
def populate_planet():

    URL_PEOPLE = "https://swapi.tech/api/planets?page=1&limit=50"
    response = request.get(URL_PEOPLE)
    data = response.json()
    for person in data["results"]:
        response = request.get(person["url"])
        person_data = response.json()
        person_data = person_data["result"]

        people = Planet()
        people.name = person_data["properties"]["name"]
        people.description = person_data["description"]
        # people.eye_color = person_data["properties"]["eye_color"]

        db.session.add(people)

    try:
        db.session.commit()
        return jsonify("People saved"), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}")
    

    
# 2) PARA PLANET:

@app.route("/people-population",  methods=["GET"])
def populate_people():

    URL_PEOPLE = "https://swapi.tech/api/people?page=1&limit=50"
    response = requests.get(URL_PEOPLE)
    data = response.json()
    for person in data["results"]:
        response = requests.get(person["url"])
        person_data = response.json()
        person_data = person_data["result"]

        people = People()
        people.name = person_data["properties"]["name"]
        people.description = person_data["description"]
        people.eye_color = person_data["properties"]["eye_color"]

        db.session.add(people)

    try:
        db.session.commit()
        return jsonify("People saved"), 201

    except Exception as error:
        db.session.rollback()
        return jsonify(f"Error: {error.args}")