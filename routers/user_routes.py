from flask import Blueprint
from controllers.user_controller import register_user

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/register', methods=['POST'])
def register():
    return register_user()
