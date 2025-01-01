Restaurant Management System
Overview
The Restaurant Management System is a web-based application designed to streamline operations in restaurants. It provides features for managing menus, handling orders, user authentication, and more. This system is built using Python and Flask and employs a relational database for data storage.

Features
User authentication with JWT (JSON Web Tokens).
CRUD operations for managing restaurant menus and orders.
SQLite database integration.
Blacklisting of JWT tokens for secure user sessions.
Modular design with organized routes and models.
Dockerized for easy deployment and scalability.

Tech Stack
Backend: Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended
Database: SQLite
Tools: Docker
Testing Tools: Postman (for API testing)

File Structure
restaurant_management_system/
├── app.py                # Main application file
├── Dockerfile            # Instructions for Dockerizing the app
├── extensions.py         # JWT token blacklist functionality 
├── models.py             # database models
├── routes.py             # route files 
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates for the app (my application dont have any frontend)
└── static/               # Static files like CSS, JS, images

License
This project is licensed under the MIT License.

