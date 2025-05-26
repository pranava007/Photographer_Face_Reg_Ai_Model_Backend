from flask import Blueprint
from controllers.login_controller import login_user

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/api/login', methods=['POST'])
def login():
    return login_user()
