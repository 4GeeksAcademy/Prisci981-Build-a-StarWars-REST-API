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
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet

app = Flask(__name__)
app.url_map.strict_slashes = False

# Database configuration
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# ============================================
# USER ENDPOINTS
# ============================================

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get a list of all the blog post users"""
    try:
        users = User.query.all()
        return jsonify([user.serialize() for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get one single user's information"""
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    """Get all the favorites that belong to the current user"""
    # For demo purposes, using user_id=1 (first user)
    # In a real app, you'd get this from authentication/session
    current_user_id = 1
    
    try:
        user = User.query.get(current_user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        
        favorite_characters = [fav.serialize() for fav in user.favorite_characters]
        favorite_planets = [fav.serialize() for fav in user.favorite_planets]
        
        return jsonify({
            "user_id": current_user_id,
            "username": user.username,
            "favorite_characters": favorite_characters,
            "favorite_planets": favorite_planets
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# CHARACTER (PEOPLE) ENDPOINTS
# ============================================

@app.route('/people', methods=['GET'])
def get_all_people():
    """Get a list of all the people in the database"""
    try:
        characters = Character.query.all()
        return jsonify([character.serialize() for character in characters]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    """Get one single person's information"""
    try:
        character = Character.query.get(people_id)
        if character is None:
            return jsonify({"error": "Character not found"}), 404
        return jsonify(character.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/people', methods=['POST'])
def create_person():
    """Create a new character/person"""
    try:
        body = request.get_json()
        if not body:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        if not body.get('name'):
            return jsonify({"error": "Name is required"}), 400
        
        # Check if character already exists
        existing = Character.query.filter_by(name=body.get('name')).first()
        if existing:
            return jsonify({"error": "Character with this name already exists"}), 400
        
        character = Character(
            name=body.get('name'),
            height=body.get('height'),
            mass=body.get('mass'),
            hair_color=body.get('hair_color'),
            skin_color=body.get('skin_color'),
            eye_color=body.get('eye_color'),
            birth_year=body.get('birth_year'),
            gender=body.get('gender'),
            homeworld_id=body.get('homeworld_id'),
            description=body.get('description'),
            image_url=body.get('image_url')
        )
        
        db.session.add(character)
        db.session.commit()
        
        return jsonify(character.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    """Update a character/person"""
    try:
        character = Character.query.get(people_id)
        if character is None:
            return jsonify({"error": "Character not found"}), 404
        
        body = request.get_json()
        if not body:
            return jsonify({"error": "Request body is required"}), 400
        
        # Update fields if provided
        if 'name' in body:
            character.name = body['name']
        if 'height' in body:
            character.height = body['height']
        if 'mass' in body:
            character.mass = body['mass']
        if 'hair_color' in body:
            character.hair_color = body['hair_color']
        if 'skin_color' in body:
            character.skin_color = body['skin_color']
        if 'eye_color' in body:
            character.eye_color = body['eye_color']
        if 'birth_year' in body:
            character.birth_year = body['birth_year']
        if 'gender' in body:
            character.gender = body['gender']
        if 'homeworld_id' in body:
            character.homeworld_id = body['homeworld_id']
        if 'description' in body:
            character.description = body['description']
        if 'image_url' in body:
            character.image_url = body['image_url']
        
        db.session.commit()
        return jsonify(character.serialize()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    """Delete a character/person"""
    try:
        character = Character.query.get(people_id)
        if character is None:
            return jsonify({"error": "Character not found"}), 404
        
        db.session.delete(character)
        db.session.commit()
        
        return jsonify({"message": f"Character {character.name} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============================================
# PLANET ENDPOINTS
# ============================================

@app.route('/planets', methods=['GET'])
def get_all_planets():
    """Get a list of all the planets in the database"""
    try:
        planets = Planet.query.all()
        return jsonify([planet.serialize() for planet in planets]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    """Get one single planet's information"""
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Planet not found"}), 404
        return jsonify(planet.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/planets', methods=['POST'])
def create_planet():
    """Create a new planet"""
    try:
        body = request.get_json()
        if not body:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        if not body.get('name'):
            return jsonify({"error": "Name is required"}), 400
        
        # Check if planet already exists
        existing = Planet.query.filter_by(name=body.get('name')).first()
        if existing:
            return jsonify({"error": "Planet with this name already exists"}), 400
        
        planet = Planet(
            name=body.get('name'),
            rotation_period=body.get('rotation_period'),
            orbital_period=body.get('orbital_period'),
            diameter=body.get('diameter'),
            climate=body.get('climate'),
            gravity=body.get('gravity'),
            terrain=body.get('terrain'),
            surface_water=body.get('surface_water'),
            population=body.get('population'),
            description=body.get('description'),
            image_url=body.get('image_url')
        )
        
        db.session.add(planet)
        db.session.commit()
        
        return jsonify(planet.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    """Update a planet"""
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Planet not found"}), 404
        
        body = request.get_json()
        if not body:
            return jsonify({"error": "Request body is required"}), 400
        
        # Update fields if provided
        if 'name' in body:
            planet.name = body['name']
        if 'rotation_period' in body:
            planet.rotation_period = body['rotation_period']
        if 'orbital_period' in body:
            planet.orbital_period = body['orbital_period']
        if 'diameter' in body:
            planet.diameter = body['diameter']
        if 'climate' in body:
            planet.climate = body['climate']
        if 'gravity' in body:
            planet.gravity = body['gravity']
        if 'terrain' in body:
            planet.terrain = body['terrain']
        if 'surface_water' in body:
            planet.surface_water = body['surface_water']
        if 'population' in body:
            planet.population = body['population']
        if 'description' in body:
            planet.description = body['description']
        if 'image_url' in body:
            planet.image_url = body['image_url']
        
        db.session.commit()
        return jsonify(planet.serialize()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    """Delete a planet"""
    try:
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Planet not found"}), 404
        
        db.session.delete(planet)
        db.session.commit()
        
        return jsonify({"message": f"Planet {planet.name} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ============================================
# FAVORITE ENDPOINTS
# ============================================

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    """Add a new favorite planet to the current user"""
    # For demo purposes, using user_id=1 (first user)
    current_user_id = 1
    
    try:
        # Check if user exists
        user = User.query.get(current_user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        
        # Check if planet exists
        planet = Planet.query.get(planet_id)
        if planet is None:
            return jsonify({"error": "Planet not found"}), 404
        
        # Check if favorite already exists
        existing_favorite = FavoritePlanet.query.filter_by(
            user_id=current_user_id, 
            planet_id=planet_id
        ).first()
        
        if existing_favorite:
            return jsonify({"error": "Planet is already in favorites"}), 400
        
        # Create new favorite
        favorite = FavoritePlanet(user_id=current_user_id, planet_id=planet_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify(favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    """Add new favorite people to the current user"""
    # For demo purposes, using user_id=1 (first user)
    current_user_id = 1
    
    try:
        # Check if user exists
        user = User.query.get(current_user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        
        # Check if character exists
        character = Character.query.get(people_id)
        if character is None:
            return jsonify({"error": "Character not found"}), 404
        
        # Check if favorite already exists
        existing_favorite = FavoriteCharacter.query.filter_by(
            user_id=current_user_id, 
            character_id=people_id
        ).first()
        
        if existing_favorite:
            return jsonify({"error": "Character is already in favorites"}), 400
        
        # Create new favorite
        favorite = FavoriteCharacter(user_id=current_user_id, character_id=people_id)
        db.session.add(favorite)
        db.session.commit()
        
        return jsonify(favorite.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    """Delete a favorite planet with the id = planet_id"""
    # For demo purposes, using user_id=1 (first user)
    current_user_id = 1
    
    try:
        favorite = FavoritePlanet.query.filter_by(
            user_id=current_user_id, 
            planet_id=planet_id
        ).first()
        
        if favorite is None:
            return jsonify({"error": "Favorite planet not found"}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({"message": "Favorite planet deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    """Delete a favorite people with the id = people_id"""
    # For demo purposes, using user_id=1 (first user)
    current_user_id = 1
    
    try:
        favorite = FavoriteCharacter.query.filter_by(
            user_id=current_user_id, 
            character_id=people_id
        ).first()
        
        if favorite is None:
            return jsonify({"error": "Favorite character not found"}), 404
        
        db.session.delete(favorite)
        db.session.commit()
        
        return jsonify({"message": "Favorite character deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)