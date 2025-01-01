from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from models import db, Dish, User, Table
from extensions import blacklist

def register_routes(app):
    # User Registration
    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()

        missing_fields = []
        required_fields = ["username","email","password","role"]
        for field in required_fields:
            if field not in data or not data[field]:
               missing_fields.append(field)

        if missing_fields:
          return jsonify({
             "error": "These fields are required:",
             "details": missing_fields
            }), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400

        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'Customer')  # Default role is Customer
        )
        user.set_password(data['password'])
        
        db.session.add(user)

        try:
            db.session.commit()
            return jsonify({"message": "User registered successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # User Login
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()

        missing_fields=[]
        required_fields=["username","email","password","role"]
        for field in required_fields:
            if field not in data or not data[field]:
               missing_fields.append(field)
        
        if missing_fields:
          return jsonify({
             "error": f"These fields are required: {', '.join(missing_fields)}"
            }), 400

        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate a JWT token using just the user.id as the identity
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "username": user.username,
            "role": user.role
        }), 200

    @app.route('/users/<int:id>', methods=['GET'])
    @jwt_required()
    def get_user(id):
        # Get the current user's identity (returns string)
        current_user_id = get_jwt_identity()
        
        # Get the current user from database
        current_user = User.query.get(current_user_id)
        
        # Check if the current user is allowed to view the requested profile
        if str(id) != current_user_id and current_user.role not in ['Admin', 'Manager']:
            return jsonify({"error": "Unauthorized"}), 403

        # Query the user from the database using the given id
        user = User.query.get_or_404(id)

        # Return user profile data
        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }), 200

    @app.route('/users', methods=['GET'])
    @jwt_required()
    def get_all_users():
        # Get the current user's identity
        current_user_id = get_jwt_identity()
        
        # Get the current user from database
        current_user = User.query.get(current_user_id)
        
        # Check if the current user is an admin (case-insensitive comparison)
        if current_user.role.lower() != 'admin':
            return jsonify({
                "error": "Unauthorized. Admin access required",
                "current_role": current_user.role
            }), 403

        # Query all users from the database
        users = User.query.all()
        
        # Return all users' data
        return jsonify({
            "users": [{
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            } for user in users]
        }), 200

    # Logout User
    @app.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        try:
            jti = get_jwt()["jti"]  # Unique identifier for the token
            blacklist.add(jti)  # Add the token's jti to the blacklist
            return jsonify({"message": "Logged out successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Add a New Dish
    @app.route('/dishes', methods=['POST'])
    @jwt_required()
    def add_dish():
        current_user_id = get_jwt_identity()
        # Fetch user from the database
        user = User.query.get(current_user_id)

        # Check if the user exists and has the required role
        if not user or user.role.lower() not in ['admin', 'manager']:
           return jsonify({"error": "Unauthorized"}), 403

        # Parse the request data
        data = request.get_json()

        
        missing_fields = []
        required_fields = ["name", "description", "price"]
        for field in required_fields:
            if field not in data or not data[field]:
               missing_fields.append(field)

        if missing_fields:
           return jsonify({
            "error": f"These fields are required: {', '.join(missing_fields)}"
           }), 400
        
        price = data.get("price")
        if not isinstance(price,(int,float)):
            return jsonify({
                "error":"invalid value",
                "details":"the 'price' field must be a number "
            })
        if price<0:
            return jsonify({
                "error":"price must be a positive number"
            }),400

        # Add dish logic
        try:
            dish = Dish(
                name=data['name'],
                description=data['description'],
                price=data['price']
            )
            db.session.add(dish)
            db.session.commit()
            return jsonify({"message": "Dish added successfully"}), 201
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return jsonify({"error": str(e)}), 500

    # View All Dishes
    @app.route('/dishes', methods=['GET'])
    def get_dishes():
        dishes = Dish.query.all()
        return jsonify([{
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price
        } for dish in dishes]), 200

    # View a Single Dish
    @app.route('/dishes/<int:id>', methods=['GET'])
    def get_dish(id):
        dish = Dish.query.get_or_404(id)
        return jsonify({
            "id": dish.id,
            "name": dish.name,
            "description": dish.description,
            "price": dish.price
        }), 200

    # Update an Existing Dish
    @app.route('/dishes/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_dish(id):
        # Get the current user's identity (returns string user_id)
        current_user_id = get_jwt_identity()
        
        # Fetch user from the database
        user = User.query.get(current_user_id)

        # Check if the user exists and has the required role
        if not user or user.role.lower() not in ['admin', 'manager']:
            return jsonify({"error": "Unauthorized"}), 403

        # Update dish logic
        try:
            dish = Dish.query.get_or_404(id)
            data = request.get_json()
            
            # Update dish attributes if provided in the request
            dish.name = data.get('name', dish.name)
            dish.description = data.get('description', dish.description)
            dish.price = data.get('price', dish.price)
            
            db.session.commit()
            return jsonify({"message": "Dish updated successfully"}), 200
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return jsonify({"error": str(e)}), 500

    # Delete a Dish
    @app.route('/dishes/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_dish(id):
        # Get the current user's identity (returns string user_id)
        current_user_id = get_jwt_identity()
        
        # Fetch user from the database
        user = User.query.get(current_user_id)

        # Check if the user exists and has the required role
        if not user or user.role.lower() not in ['admin', 'manager']:
            return jsonify({"error": "Unauthorized"}), 403

        try:
            # Find and delete the dish
            dish = Dish.query.get_or_404(id)
            db.session.delete(dish)
            db.session.commit()
            return jsonify({"message": "Dish deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return jsonify({"error": str(e)}), 500

    # Add a New Table (Admin/Manager Only)
    @app.route('/tables', methods=['POST'])
    @jwt_required()
    def add_table():
        # Get the current user's identity (returns string user_id)
        current_user_id = get_jwt_identity()
        
        # Fetch user from the database
        user = User.query.get(current_user_id)

        # Check if the user exists and has the required role
        if not user or user.role.lower() not in ['admin', 'manager']:
            return jsonify({"error": "Unauthorized"}), 403

        # Add table logic
        try:
            data = request.get_json()
            missing_fields = []
            required_fields = ["table_number", "seating_capacity", "is_available"]
            for field in required_fields:
                if field not in data or not data[field]:
                   missing_fields.append(field)

            if missing_fields:
               return jsonify({
                "error": f"These fields are required: {', '.join(missing_fields)}"
               }), 400
        
            fields_to_validate={
                "table_number":(int,float),
                "seating_capacity":(int,float)
                
            }
            for field, expected_type in fields_to_validate.items():
                value = data.get(field)
                if not isinstance(value,expected_type):
                    return jsonify({
                        "error":"invalid value",
                        "details":f"the '{field}' field must be a number"
                    }),400
        
            if value<0:
                return jsonify({
                   "error":f"the '{field}' field must be a positive number"
                }),400
            
            #fetch table number from databse

            
            table = Table(
                table_number=data['table_number'],
                seating_capacity=data['seating_capacity'],
                is_available=data.get('is_available', True)
            )
            db.session.add(table)
            db.session.commit()
            return jsonify({"message": "Table added successfully"}), 201
        except KeyError as e:
            return jsonify({"error": f"Missing required field: {str(e)}"}), 400
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return jsonify({"error": str(e)}), 500

    # View All Tables
    @app.route('/tables', methods=['GET'])
    def get_tables():
        tables = Table.query.all()
        return jsonify([{
            'id': table.id,
            'table_number': table.table_number,
            'seating_capacity': table.seating_capacity,
            'is_available': table.is_available
        } for table in tables]), 200

    # Update Table Details (Admin/Manager Only)
    @app.route('/tables/<int:id>', methods=['PUT'])
    @jwt_required()
    def update_table(id):
        # Get the current user's identity (returns string user_id)
        current_user_id = get_jwt_identity()
        
        # Fetch user from the database
        user = User.query.get(current_user_id)

        # Check if the user exists and has the required role
        if not user or user.role.lower() not in ['admin', 'manager']:
            return jsonify({"error": "Unauthorized"}), 403

        try:
            # Find and update the table
            table = Table.query.get_or_404(id)
            data = request.get_json()
            
            # Update table attributes if provided in the request
            table.table_number = data.get('table_number', table.table_number)
            table.seating_capacity = data.get('seating_capacity', table.seating_capacity)
            table.is_available = data.get('is_available', table.is_available)
            
            db.session.commit()
            return jsonify({"message": "Table updated successfully"}), 200
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return jsonify({"error": str(e)}), 500

    # Delete a Table (Admin/Manager Only)
    @app.route('/tables/<int:id>', methods=['DELETE'])
    @jwt_required()
    def delete_table(id):
        # Get the current user's identity (returns string user_id)
        current_user_id = get_jwt_identity()
        
        # Fetch user from the database
        user = User.query.get(current_user_id)

        # Check if the user exists and has the required role
        if not user or user.role.lower() not in ['admin', 'manager']:
            return jsonify({"error": "Unauthorized"}), 403

        try:
            # Find and delete the table
            table = Table.query.get_or_404(id)
            db.session.delete(table)
            db.session.commit()
            return jsonify({"message": "Table deleted successfully"}), 200
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return jsonify({"error": str(e)}), 500
