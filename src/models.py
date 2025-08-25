from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """
    User model for blog authentication and favorites
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    favorite_characters = db.relationship('FavoriteCharacter', backref='user', lazy=True, cascade='all, delete-orphan')
    favorite_planets = db.relationship('FavoritePlanet', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }

class Character(db.Model):
    """
    StarWars characters model (people)
    """
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    height = db.Column(db.String(10))  # e.g., "172"
    mass = db.Column(db.String(10))    # e.g., "77"
    hair_color = db.Column(db.String(50))
    skin_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    birth_year = db.Column(db.String(20))  # e.g., "19BBY"
    gender = db.Column(db.String(20))
    homeworld_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    homeworld = db.relationship('Planet', backref='native_characters', foreign_keys=[homeworld_id])
    favorite_by_users = db.relationship('FavoriteCharacter', backref='character', lazy=True)
    
    def __repr__(self):
        return f'<Character {self.name}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld": self.homeworld.serialize() if self.homeworld else None,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Planet(db.Model):
    """
    StarWars planets model
    """
    __tablename__ = 'planets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rotation_period = db.Column(db.String(20))  # hours
    orbital_period = db.Column(db.String(20))   # days
    diameter = db.Column(db.String(20))         # km
    climate = db.Column(db.String(100))
    gravity = db.Column(db.String(50))
    terrain = db.Column(db.String(200))
    surface_water = db.Column(db.String(10))    # percentage
    population = db.Column(db.String(20))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    favorite_by_users = db.relationship('FavoritePlanet', backref='planet', lazy=True)
    
    def __repr__(self):
        return f'<Planet {self.name}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "diameter": self.diameter,
            "climate": self.climate,
            "gravity": self.gravity,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "population": self.population,
            "description": self.description,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class FavoriteCharacter(db.Model):
    """
    Many-to-many relationship table for user favorite characters
    """
    __tablename__ = 'favorite_characters'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate favorites
    __table_args__ = (db.UniqueConstraint('user_id', 'character_id', name='unique_user_character'),)
    
    def __repr__(self):
        return f'<FavoriteCharacter User:{self.user_id} Character:{self.character_id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "character": self.character.serialize() if self.character else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class FavoritePlanet(db.Model):
    """
    Many-to-many relationship table for user favorite planets
    """
    __tablename__ = 'favorite_planets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate favorites
    __table_args__ = (db.UniqueConstraint('user_id', 'planet_id', name='unique_user_planet'),)
    
    def __repr__(self):
        return f'<FavoritePlanet User:{self.user_id} Planet:{self.planet_id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "planet": self.planet.serialize() if self.planet else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }