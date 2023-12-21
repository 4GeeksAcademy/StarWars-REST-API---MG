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
from models import db, User, Planet, Character, Favorite

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


"""         Status codes
200 OK: Successful GET requests.
201 Created: Successful POST requests.
204 No Content: Successful DELETE requests with no additional content to return.
400 Bad Request: Invalid data or missing parameters in the request body.
404 Not Found: The requested resource (user, planet, character, etc.) is not found.
409 Conflict: Indicates a conflict, such as trying to add a resource that already exists in the list of favorites.
"""


@app.route("/user", methods=["GET"])
def get_users():
    users = User.query.all()
    serialized_users = list(map(lambda item: item.serialize(), users))
    return jsonify({"msg": "ok", "results": serialized_users}), 200


@app.route("/user/<int:user_id>", methods=["GET"])
def get_single_user(user_id):
    user = User.query.get(user_id)
    serialized_user = user.serialize()
    return jsonify({"msg": "ok", "result": serialized_user}), 200


@app.route("/user/", methods=["POST"])
def create_user():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "You must put information in the body"}), 400
    if "user_name" not in body:
        return jsonify({"msg": "Falta el parametro username"}), 400
    if "email" not in body:
        return jsonify({"msg": "Falta el parametro email"}), 400
    if "password" not in body:
        return jsonify({"msg": "Falta el parametro password"}), 400
    if "is_active" not in body:
        return jsonify({"msg": "Falta el parametro is active"}), 400
    new_user = User()
    new_user.user_name = body["user_name"]
    new_user.email = body["email"]
    new_user.password = body["password"]
    new_user.is_active = body["is_active"]
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Added successfully"}), 201


@app.route("/user/<int:user_id>", methods=["PUT"])
def update_single_user(user_id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "User not found"}), 404
    if "user_name" not in body:
        return jsonify({"msg": "user_name parameter is required"}), 400
    if "email" not in body:
        return jsonify({"msg": "email parameter is required"}), 400
    if "password" not in body:
        return jsonify({"msg": "password parameter is required"}), 400
    if "is_active" not in body:
        return jsonify({"msg": "is_active parameter is required"}), 400
    user = User.query.get(user_id)
    user.user_name = body["user_name"]
    user.email = body["email"]
    user.password = body["password"]
    user.is_active = body["is_active"]
    db.session.commit()
    return jsonify({"msg": "Updated successfully"}), 200


@app.route("/user/<int:user_id>", methods=["DELETE"])
def delete_single_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    else:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User deleted successfully"}), 200


@app.route("/planet", methods=["GET"])
def get_planets():
    planets = Planet.query.all()
    serialized_planets = list(map(lambda item: item.serialize(), planets))
    return jsonify({"msg": "ok", "results": serialized_planets}), 200


@app.route("/planet/<int:planet_id>", methods=["GET"])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    serialized_planet = planet.serialize()
    return jsonify({"msg": "ok", "result": serialized_planet}), 200


@app.route("/planet/", methods=["POST"])
def create_planet():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "You must put information in the body"}), 400
    if "name" not in body:
        return jsonify({"msg": "name parameter is required"}), 400
    if "is_active" not in body:
        return jsonify({"msg": "is_active parameter is required"}), 400
    new_planet = Planet()
    new_planet.name = body["name"]
    new_planet.is_active = body["is_active"]
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "Added successfully"}), 201


@app.route("/planet/<int:planet_id>", methods=["PUT"])
def update_single_planet(planet_id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "Planet not found"}), 404
    if "name" not in body:
        return jsonify({"msg": "name parameter is required"}), 400
    if "is_active" not in body:
        return jsonify({"msg": "is_active parameter is required"}), 400
    planet = Planet.query.get(planet_id)
    planet.name = body["name"]
    planet.is_active = body["is_active"]
    db.session.commit()
    return jsonify({"msg": "Updated successfully"}), 200


@app.route("/planet/<int:planet_id>", methods=["DELETE"])
def delete_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    else:
        db.session.delete(planet)
        db.session.commit()
        return jsonify({"msg": "Planet deleted successfully"}), 200


@app.route("/character/", methods=["GET"])
def get_characters():
    characters = Character.query.all()
    serialized_characters = list(map(lambda item: item.serialize(), characters))
    return jsonify({"msg": "ok", "results": serialized_characters}), 200


@app.route("/character/<int:character_id>", methods=["GET"])
def get_single_character(character_id):
    character = Character.query.get(character_id)
    serialized_character = character.serialize()
    return jsonify({"msg": "ok", "result": serialized_character}), 200


@app.route("/character/", methods=["POST"])
def create_character():
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "You must put information in the body"}), 400
    if "name" not in body:
        return jsonify({"msg": "name parameter is required"}), 400
    if "homeworld_id" not in body:
        return jsonify({"msg": "homeworld_id parameter is required"}), 400
    if "is_active" not in body:
        return jsonify({"msg": "is_active parameter is required"}), 400
    new_character = Character()
    new_character.name = body["name"]
    new_character.homeworld_id = body["homeworld_id"]
    new_character.is_active = body["is_active"]
    db.session.add(new_character)
    db.session.commit()
    return jsonify({"msg": "Added successfully"}), 201


@app.route("/character/<int:character_id>", methods=["PUT"])
def update_single_character(character_id):
    body = request.get_json(silent=True)
    if body is None:
        return jsonify({"msg": "Character not found"}), 404
    if "name" not in body:
        return jsonify({"msg": "name parameter is required"}), 400
    if "homeworld_id" not in body:
        return jsonify({"msg": "homeworld parameter is required"}), 400
    if "is_active" not in body:
        return jsonify({"msg": "is_active parameter is required"}), 400
    character = Character.query.get(character_id)
    character.name = body["name"]
    character.homeworld_id = body["homeworld_id"]
    character.is_active = body["is_active"]
    db.session.commit()
    return jsonify({"msg": "Updated successfully"}), 200


@app.route("/character/<int:character_id>", methods=["DELETE"])
def delete_single_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": "Character not found"}), 404
    else:
        db.session.delete(character)
        db.session.commit()
        return jsonify({"msg": "Character deleted successfully"}), 200


@app.route("/favorites/user/<int:user_id>", methods=["GET"])
def get_favorites(user_id):
    user = User.query.get(user_id)
    if user is None:
        return (
            jsonify({"msg": "The user with id {} doesn't exist".format(user_id)}),
            404,
        )
    favorite_planets = (
        db.session.query(Favorite, Planet)
        .join(Planet)
        .filter(Favorite.user_id == user_id)
        .all()
    )

    favorite_planets_serialize = []
    for favorite_planet, planet_item in favorite_planets:
        favorite_planets_serialize.append({"planet": planet_item.serialize()})

    favorite_characters = (
        db.session.query(Favorite, Character)
        .join(Character)
        .filter(Favorite.user_id == user_id)
        .all()
    )
    favorite_characters_serialize = []
    for favorite_character, character_item in favorite_characters:
        favorite_characters_serialize.append({"character": character_item.serialize()})

    return (
        jsonify(
            {
                "msg": "ok",
                "user": user.serialize(),
                "Favorite planets": favorite_planets_serialize,
                "Favorite characters": favorite_characters_serialize,
            }
        ),
        200,
    )


@app.route("/favorite/user/<int:user_id>/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None:
        return (
            jsonify({"msg": "The user with id {} doesn't exist".format(user_id)}),
            404,
        )
    if planet is None:
        return (
            jsonify({"msg": "The planet with id {} doesn't exist".format(planet_id)}),
            404,
        )

    favorite_planets = (
        db.session.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.planet_id == planet_id)
        .first()
    )

    if favorite_planets:
        return jsonify({"msg": "It's already on favorites list"}), 409

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added successfully"}), 201


@app.route("/favorite/user/<int:user_id>/planet/<int:planet_id>", methods=["DELETE"])
def delete_favorite_planet(user_id, planet_id):
    favorite = (
        db.session.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.planet_id == planet_id)
        .first()
    )

    if favorite is None:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted successfully"}), 200


@app.route(
    "/favorite/user/<int:user_id>/character/<int:character_id>", methods=["POST"]
)
def add_favorite_character(user_id, character_id):
    user = User.query.get(user_id)
    character = Character.query.get(character_id)

    if user is None:
        return (
            jsonify({"msg": "The user with id {} doesn't exist".format(user_id)}),
            404,
        )
    if character is None:
        return (
            jsonify(
                {"msg": "The character with id {} doesn't exist".format(character_id)}
            ),
            404,
        )

    favorite_character = (
        db.session.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.character_id == character_id)
        .first()
    )

    if favorite_character:
        return jsonify({"msg": "It's already on favorites list"}), 409

    new_favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"msg": "Favorite character added successfully"}), 201


@app.route(
    "/favorite/user/<int:user_id>/character/<int:character_id>", methods=["DELETE"]
)
def delete_favorite_character(user_id, character_id):
    favorite = (
        db.session.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.character_id == character_id)
        .first()
    )

    if favorite is None:
        return jsonify({"msg": "Favorite character not found"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite character deleted successfully"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT, debug=False)
