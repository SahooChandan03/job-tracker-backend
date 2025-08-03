from flask import request, jsonify
from . import auth_bp
from .jwt import get_current_user
from ..schemas import UserCreate, UserLogin, UserResponse, VerifyOTP, ResendOTP, ForgetPassword, ResetPassword
from ..services.user_service import UserService
from pydantic import ValidationError
import warnings

# Suppress bcrypt version warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*")

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = UserCreate(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    print(data,"data")
    try:
        result = UserService.register_user(data)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route("/verify-otp", methods=['POST'])
def verify_otp():
    """Verify OTP and activate user."""
    try:
        data = VerifyOTP(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        result = UserService.verify_otp(data)
        return jsonify({
            'user': UserResponse.model_validate(result['user']).model_dump(),
            'access_token': result['access_token'],
            'token_type': result['token_type']
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': e}), 500

@auth_bp.route("/resend-otp", methods=['POST'])
def resend_otp():
    """Resend OTP to user's email for any module."""
    try:
        data = ResendOTP(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        result = UserService.resend_otp(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'OTP resend failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = UserLogin(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        result = UserService.login_user(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/me', methods=['GET'])
def me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Invalid or missing token'}), 401
    
    return jsonify({
        'user': UserResponse.model_validate(user).model_dump()
    }), 200

@auth_bp.route('/forget-password', methods=['POST'])
def forget_password():
    """Send OTP for password reset."""
    try:
        data = ForgetPassword(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        result = UserService.forget_password(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Password reset request failed'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using OTP."""
    try:
        data = ResetPassword(**request.get_json())
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        result = UserService.reset_password(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Password reset failed'}), 500 