from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from database import init_db
# from routers.upload_routes import upload_bp
from routers.user_routes import user_bp
from routers.login_routes import login_bp
from routers.event_routes import event_bp
from routers.test_routes import test_bp

# Load environment variables
load_dotenv()

# Initialize JWT
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')



    # App Config
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI')  # Optional if using direct URI
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

    # ✅ Enable CORS with dynamic frontend origin and credentials support
    
    CORS(app, supports_credentials=True, origins=[os.getenv('FRONTEND_URL', 'https://photograperfaceai.netlify.app')])

    # Init DB and JWT
    init_db(app)
    jwt.init_app(app)

    # Register all Blueprints     upload_bp , this is commend router upload_router and controller upload_controller 
    # for bp in [user_bp, login_bp, event_bp, upload_bp , test_bp]:
    for bp in [user_bp, login_bp, event_bp,  test_bp]:
        app.register_blueprint(bp, url_prefix="/")

    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
  
   
