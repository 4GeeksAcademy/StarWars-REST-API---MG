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
from models import db, User, Planet, Character

# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace(
        "postgres://", "postgresql://"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
@app.route("/")
def sitemap():
    return generate_sitemap(app)


@app.route("/user", methods=["GET"])
def get_users():
    users = User.query.all()
    serialized_users = list(map(lambda item: item.serialize(), users))
    return jsonify({"msg": "ok", "results": serialized_users}), 200


@app.route("/user/", methods=["POST"])
@app.route("/user/<int:character_id>", methods=["PUT"])
@app.route("/user/<int:character_id>", methods=["DELETE"])
@app.route("/planet", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = list(map(lambda item: item.serialize(), planets))
    return jsonify({"msg": "ok", "results": serialized_planets}), 200


@app.route("/planet/<int:planet_id", methods=["GET"])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    serialized_planet = planet.serialize()
    return jsonify({"msg": "ok", "result": serialized_planet})


@app.route("/planet/", methods=["POST"])
@app.route("/planet/<int:planet_id>", methods=["PUT"])
@app.route("/planet/<int:planet_id>", methods=["DELETE"])
@app.route("/character", methods=["GET"])
def get_characters():
    characters = Character.query.all()
    serialized_characters = list(map(lambda item: item.serialize(), characters))
    return jsonify({"msg": "ok", "results": serialized_characters}), 200


@app.route("/character/<int:character_id", methods=["GET"])
def get_single_character(character_id):
    character = Character.query.get(character_id)
    serialized_character = character.serialize()
    return jsonify({"msg": "ok", "result": serialized_character})


@app.route("/character/", methods=["POST"])
def create_character():
    body = request.get_json(slient=True)
    if body is None:
        return jsonify({"msg": "Debes poner informacion en el body"}), 400
    if "name" not in body:
        return jsonify({"msg": "Falta el parametro name"}), 400
    if "homeworld_id" not in body:
        return jsonify({"msg": "Falta el parametro homeworld"}), 404
    new_character = Character()
    new_character.name = body["name"]
    new_character.homeworld_id = body["homeworld_id"]
    db.session.add(new_character)
    db.session.commit()
    return jsonify({"msg": "Agregado correctamente"}), 200


@app.route("/character/<int:character_id>", methods=["PUT"])
def update_single_character(character_id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "Character not found"}), 404
    if "name" not in body:
        return jsonify({"msg": "Se debe enviar nombre"}), 404
    if "homeworld_id" not in body:
        return jsonify({"msg": "Se debe ingresar homeworld"}), 404
    character = Character.query.get(character_id)
    character.name = body["name"]
    character.homeworld_id = body["homeworld_id"]
    db.session.commit()
    return jsonify({"msg": "Actualizado correctamente"})


@app.route("/character/<int:character_id>", methods=["DELETE"])
def delete_single_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": "Character not found"}), 404
    else:
        db.session.delete(character)
        db.session.commit()


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
