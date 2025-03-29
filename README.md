I'll create a comprehensive README for your Flask project "Cookie King" based on the code files provided. Let me analyze the project structure, dependencies, and functionality first.

# Cookie King

Cookie King is a web application for managing a cookie production system. It allows users to handle cookie recipes, ingredients inventory, production processes, and sales tracking.

## Project Overview

This application is built with Flask and uses a MySQL database with SQLAlchemy ORM. The frontend is styled using Tailwind CSS and Flowbite components. The system is organized into modules following a Model-View-Controller (MVC) pattern.

## Features

- **Cookie Management**: Create, read, update, and delete cookie types
- **Recipe Management**: Create and manage recipes with ingredients and instructions
- **Ingredient Management**: Track ingredients inventory and suppliers
- **Production Tracking**: Plan and monitor cookie production
- **Sales Management**: Register and query cookie sales (individual or packages)
- **User-friendly Interface**: Modern, responsive UI with TailwindCSS

## Project Structure

The application is organized into modules:
- `modulos/galletas`: Cookie type management
- `modulos/recetas`: Recipe management
- `modulos/ingredientes`: Ingredient inventory management
- Future modules planned: Production, Sales, Reports

## Prerequisites

- Python 3.7+
- MySQL Database
- Node.js (for TailwindCSS)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/IDGS-803-22001409/CookieKing
   cd cookie-king
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On Linux/Mac
   source env/bin/activate
   ```

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Node.js dependencies:
   ```
   npm install
   ```

5. Configure your database connection in `config.py`:
   ```python
   # Update the following line with your database credentials
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost:3306/CookieKing'
   ```

6. Initialize the database:
   ```
   python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

## Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Access the application in your browser at:
   ```
   http://localhost:5000
   ```

## Technologies Used

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-WTF**: Form handling and validation
- **PyMySQL**: MySQL connector for Python

### Frontend
- **TailwindCSS**: Utility-first CSS framework
- **Flowbite**: UI component library built on top of TailwindCSS
- **JavaScript**: Client-side interactivity

### Database
- **MySQL**: Relational database system

## Technical Details

### Dependencies

The project uses the following Python packages:
- Flask (3.0.1)
- Flask-SQLAlchemy (3.1.1)
- Flask-WTF (1.2.1)
- PyMySQL (1.1.0)
- WTForms (3.1.2)
- And others as listed in requirements.txt

For frontend development:
- Tailwind CSS (4.0.14)
- Flowbite (3.1.2)

### Database Schema

The application uses several related tables:
- `Galletas`: Cookie types
- `Recetas`: Recipes
- `Ingredientes`: Ingredients
- `RecetaIngredientes`: Relationship between recipes and ingredients
- Other supporting tables for sales, production, etc.

## Development

### Adding a New Module

1. Create a new directory under `modulos/`
2. Implement the module structure with models, controllers, routes, and templates
3. Register the module's blueprint in `routes.py`

### Application Flow

The application follows a standard MVC pattern:
1. Routes receive HTTP requests
2. Controllers handle business logic
3. Models interact with the database
4. Templates render the user interface

## Future Enhancements

- User authentication and authorization
- Reporting and analytics
- Inventory alerts
- Production scheduling
- Order management
- Customer relationship management

## License

[Your License Information Here]

---

This README provides an overview of the Cookie King application. For more detailed documentation, please refer to the code comments and module-specific documentation.