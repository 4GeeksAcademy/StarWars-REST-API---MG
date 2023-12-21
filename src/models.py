from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return "{}".format(self.user_name)

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    __tablename__ = "planet"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.Integer)
    terrain = db.Column(db.String(80))
    climate = db.Column(db.String(80))
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return "{}".format(self.name)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "terrain": self.terrain,
            "climate": self.climate,
            "is_active": self.is_active,
        }


class Character(db.Model):
    __tablename__ = "character"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.Float)
    mass = db.Column(db.Float)
    birth_year = db.Column(db.String(50))
    homeworld_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=False)
    homeworld = db.relationship("Planet")
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return "{}".format(self.name)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "birth_year": self.birth_year,
            "homeworld": self.homeworld.serialize(),
            "is_active": self.is_active,
        }


class Starship(db.Model):
    __tablename__ = "starship"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    model = db.Column(db.String(64))
    starship_type = db.Column(db.String(64))
    pilot_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    pilot = db.relationship("Character")
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return "{}".format(self.name)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "starship_type": self.starship_type,
            "pilot": self.pilot.serialize() if self.pilot else None,
            "is_active": self.is_active,
        }


class Vehicle(db.Model):
    __tablename__ = "vehicle"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    model = db.Column(db.String(64))
    vehicle_type = db.Column(
        db.Enum("Squad transport", "Speeder bike", name="vehicle_types")
    )
    pilot_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    pilot = db.relationship("Character")
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return "{}".format(self.name)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "vehicle_type": self.vehicle_type.value,
            "pilot": self.pilot.serialize() if self.pilot else None,
            "is_active": self.is_active,
        }


class FilmData(db.Model):
    __tablename__ = "film_data"
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"))
    character = db.relationship("Character")
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"))
    planet = db.relationship("Planet")
    starship_id = db.Column(db.Integer, db.ForeignKey("starship.id"))
    starship = db.relationship("Starship")
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id"))
    vehicle = db.relationship("Vehicle")

    def __repr__(self):
        return "Datos de pelicula {}".format(self.id)

    def serialize(self):
        return {
            "id": self.id,
            "character": self.character.serialize() if self.character else None,
            "planet": self.planet.serialize() if self.planet else None,
            "starship": self.starship.serialize() if self.starship else None,
            "vehicle": self.vehicle.serialize() if self.vehicle else None,
        }


class Film(db.Model):
    __tablename__ = "film"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    film_data_id = db.Column(db.Integer, db.ForeignKey("film_data.id"))
    film_data = db.relationship("FilmData")
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return "{}".format(self.title)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "info": self.film_data.serialize() if self.film_data else None,
            "is_active": self.is_active,
        }


class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")
    character_id = db.Column(db.Integer, db.ForeignKey("character.id"), nullable=True)
    character = db.relationship("Character")
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), nullable=True)
    planet = db.relationship("Planet")
    starship_id = db.Column(db.Integer, db.ForeignKey("starship.id"), nullable=True)
    starship = db.relationship("Starship")
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id"), nullable=True)
    vehicle = db.relationship("Vehicle")
    film_id = db.Column(db.Integer, db.ForeignKey("film.id"), nullable=True)
    film = db.relationship("Film")
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "character_id",
            "planet_id",
            "starship_id",
            "vehicle_id",
            "film_id",
            name="uq_user_favorites",
        ),
        db.UniqueConstraint(
            "user_id",
            "character_id",
            "planet_id",
            name="uq_user_char_planet",
        ),
        db.UniqueConstraint(
            "user_id",
            "character_id",
            name="uq_user_character",
        ),
        db.UniqueConstraint(
            "user_id",
            "planet_id",
            name="uq_user_planet",
        ),
    )

    def __repr__(self):
        return "{}".format(self.user_id.user_name)

    def serialize(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_id.user_name,
            "type": "Favorito",
            "object_id": self.character_id
            or self.planet_id
            or self.starship_id
            or self.vehicle_id
            or self.film_id,
        }
