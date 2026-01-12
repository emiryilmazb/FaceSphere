from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from extensions import db
from routes import main_routes, admin_routes


def create_app():
    app = Flask(__name__)
    app.secret_key = 'FaceSphere'
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    db.init_app(app)

    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from database_models import User, AccessLog
        db.create_all()

    app.register_blueprint(main_routes.bp)
    app.register_blueprint(admin_routes.bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
