from passlib.hash import bcrypt
from ..models import User
from ..schemas import UserCreate, UserLogin, VerifyOTP, ResendOTP, ForgetPassword, ResetPassword
from ..config.database import db
from ..config.redis import get_sync_redis
from ..config.security import generate_otp, check_otp_limit, increment_otp_count, reset_otp_limit, get_otp_remaining_time
from ..config.email import send_otp_email, send_password_reset_email
from ..auth.jwt import create_access_token
from typing import Optional, Tuple, Dict, Any
import warnings

# Suppress bcrypt version warnings
warnings.filterwarnings("ignore", message=".*bcrypt.*")

class UserService:
    @staticmethod
    def register_user(user_data: UserCreate) -> Dict[str, Any]:
        """Register a new user with OTP verification"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data.email).first()
        
        if existing_user and existing_user.is_active:
            raise ValueError("User with this email already exists")
        
        sync_redis = get_sync_redis()
        
        if existing_user and not existing_user.is_active:
            return UserService._handle_inactive_user_registration(user_data, sync_redis)
        
        # Create new user
        password_hash = bcrypt.hash(user_data.password)
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        return UserService._handle_new_user_registration(user_data, sync_redis)
    
    @staticmethod
    def _handle_inactive_user_registration(user_data: UserCreate, sync_redis) -> Dict[str, Any]:
        """Handle registration for inactive users"""
        # Check if user is blocked
        block_key = f"blocked_user:register:{user_data.email}"
        is_blocked = sync_redis.get(block_key)
        
        if is_blocked:
            remaining_block_time = sync_redis.ttl(block_key)
            minutes = remaining_block_time // 60
            seconds = remaining_block_time % 60
            raise ValueError(f"Account temporarily blocked. Please try again in {minutes}m {seconds}s")
        
        # Check OTP rate limit for inactive user
        can_request, attempts_remaining = check_otp_limit(sync_redis, user_data.email, "register")
        
        if not can_request:
            # Block user for 20 minutes (1200 seconds)
            sync_redis.setex(block_key, 1200, "blocked")
            sync_redis.delete(f"otp:register:{user_data.email}")
            sync_redis.delete(f"otp_limit:register:{user_data.email}")
            raise ValueError("OTP limit exceeded. Account blocked for 20 minutes.")
        
        # Generate and send OTP
        otp = generate_otp()
        sync_redis.set(f"otp:register:{user_data.email}", otp, ex=300)  # 5 minutes expiry
        increment_otp_count(sync_redis, user_data.email, "register")
        send_otp_email(user_data.email, otp)
        
        return {
            "message": "OTP sent successfully",
            "attempts_remaining": attempts_remaining - 1
        }
    
    @staticmethod
    def _handle_new_user_registration(user_data: UserCreate, sync_redis) -> Dict[str, Any]:
        """Handle registration for new users"""
        # Check OTP rate limit for registration
        can_request, attempts_remaining = check_otp_limit(sync_redis, user_data.email, "register")
        
        if not can_request:
            remaining_time = get_otp_remaining_time(sync_redis, user_data.email, "register")
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            raise ValueError(f"OTP limit exceeded. Please try again in {hours}h {minutes}m")
        
        # Generate and send OTP
        otp = generate_otp()
        sync_redis.set(f"otp:register:{user_data.email}", otp, ex=300)  # 5 minutes expiry
        increment_otp_count(sync_redis, user_data.email, "register")
        send_otp_email(user_data.email, otp)
        
        return {
            "message": "OTP sent successfully",
            "attempts_remaining": attempts_remaining - 1
        }
    
    @staticmethod
    def verify_otp(otp_data: VerifyOTP) -> Dict[str, Any]:
        """Verify OTP and activate user"""
        # Find user
        user = User.query.filter_by(email=otp_data.email).first()
        if not user:
            raise ValueError("User not found")
        
        # Get OTP from Redis
        sync_redis = get_sync_redis()
        if not sync_redis:
            raise ValueError("Redis connection failed")
        module = otp_data.module
        # Check if user is blocked due to wrong OTP attempts
        otp_block_key = f"blocked_user:{module}:{otp_data.email}"
        is_otp_blocked = sync_redis.get(otp_block_key)
        
        if is_otp_blocked:
            remaining_block_time = sync_redis.ttl(otp_block_key)
            minutes = remaining_block_time // 60
            seconds = remaining_block_time % 60
            raise ValueError(f"Account blocked due to multiple wrong OTP attempts. Please try again in {minutes}m {seconds}s")
        
        # Check if user is blocked for OTP requests
        block_key = f"blocked_user:{otp_data.email}"
        is_blocked = sync_redis.get(block_key)
        
        if is_blocked:
            remaining_block_time = sync_redis.ttl(block_key)
            minutes = remaining_block_time // 60
            seconds = remaining_block_time % 60
            raise ValueError(f"Account temporarily blocked. Please try again in {minutes}m {seconds}s")
        
        # Get OTP from Redis using module-based key
        otp_key = f"otp:{module}:{otp_data.email}"
        stored_otp = sync_redis.get(otp_key)
        if stored_otp is None or stored_otp != otp_data.code:
            # Increment wrong OTP attempt count using module-based key
            wrong_attempt_key = f"wrong_otp_attempts:{otp_data.email}:{module}"
            current_attempts = sync_redis.get(wrong_attempt_key)
            
            if current_attempts is None:
                # First wrong attempt
                sync_redis.setex(wrong_attempt_key, 3600, 1)  # 1 hour window
            else:
                attempts = int(current_attempts) + 1
                if attempts >= 5:  # Block after 5 wrong attempts
                    # Block user for 30 minutes (1800 seconds)
                    sync_redis.setex(otp_block_key, 1800, "blocked")
                    sync_redis.delete(wrong_attempt_key)
                    raise ValueError("Account blocked due to multiple wrong OTP attempts. Please try again in 30 minutes.")
                else:
                    sync_redis.incr(wrong_attempt_key)
            
            raise ValueError("Invalid OTP")
        
        # OTP is correct - reset wrong attempt counter and proceed
        sync_redis.delete(f"wrong_otp_attempts:{otp_data.email}:{module}")
        
        # Handle different modules
        if module == "register":
            # Activate user for registration
            user.is_active = True
            db.session.commit()
        elif module == "login":
            # For login, just verify the user is active
            if not user.is_active:
                raise ValueError("User account is deactivated")
        elif module == "forgetpassword":
            # For password reset, just verify the user exists
            pass
        
        # Delete OTP from Redis
        sync_redis.delete(otp_key)
        reset_otp_limit(sync_redis, otp_data.email, module)
        
        # Unblock user if they were blocked
        sync_redis.delete(block_key)
        sync_redis.delete(otp_block_key)
        
        # Generate access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {
            "user": user,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def resend_otp(resend_data: ResendOTP) -> Dict[str, Any]:
        """Resend OTP for any module"""
        # Validate module
        valid_modules = ["register", "login", "forgetpassword"]
        if resend_data.module.lower() not in valid_modules:
            raise ValueError(f"Invalid module. Must be one of: {', '.join(valid_modules)}")
        
        # Check if user exists (for register module, user might not exist yet)
        user = User.query.filter_by(email=resend_data.email).first()
        if resend_data.module.lower() != "register":
            if not user:
                raise ValueError("User not found")
            elif not user.is_active and resend_data.module in ["login", "forgetpassword"]:
                raise ValueError("User account is deactivated")
        
        sync_redis = get_sync_redis()
        
        # Check if user is blocked for the module (includes both OTP requests and resend attempts)
        block_key = f"blocked_user:{resend_data.module}:{resend_data.email}"
        is_blocked = sync_redis.get(block_key)
        
        if is_blocked:
            remaining_block_time = sync_redis.ttl(block_key)
            minutes = remaining_block_time // 60
            seconds = remaining_block_time % 60
            raise ValueError(f"Account temporarily blocked. Please try again in {minutes}m {seconds}s")
        
        # Check OTP rate limit for the specific module
        can_request, attempts_remaining = check_otp_limit(sync_redis, resend_data.email, resend_data.module)
        
        if not can_request:
            # Block user based on module
            if resend_data.module.lower() == "register":
                # 20 minutes for register module
                sync_redis.setex(block_key, 1200, "blocked")
                raise ValueError(f"OTP limit exceeded for {resend_data.module}. Account blocked for 20 minutes.")
            else:
                # 24 hours for other modules
                sync_redis.setex(block_key, 86400, "blocked")
                raise ValueError(f"OTP limit exceeded for {resend_data.module}. Account blocked for 24 hours.")
        
        # Generate and send new OTP
        otp = generate_otp()
        
        # Store OTP in Redis using module-based key
        otp_key = f"otp:{resend_data.module}:{resend_data.email}"
        sync_redis.set(otp_key, otp, ex=300)  # 5 minutes expiry
        increment_otp_count(sync_redis, resend_data.email, resend_data.module)
        
        send_otp_email(resend_data.email, otp)
        
        return {
            "message": f"OTP sent successfully for {resend_data.module}",
            "module": resend_data.module,
            "attempts_remaining": attempts_remaining - 1
        }
    
    @staticmethod
    def login_user(login_data: UserLogin) -> Dict[str, Any]:
        """Login user with email and password, sends OTP for verification"""
        # Find user
        user = User.query.filter_by(email=login_data.email).first()
        if not user or not bcrypt.verify(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        if not user.is_active:
            raise ValueError("User account is deactivated")
        
        # Check if user is blocked for login attempts
        sync_redis = get_sync_redis()
        block_key = f"blocked_user:login:{login_data.email}"
        is_blocked = sync_redis.get(block_key)
        
        if is_blocked:
            remaining_block_time = sync_redis.ttl(block_key)
            minutes = remaining_block_time // 60
            seconds = remaining_block_time % 60
            raise ValueError(f"Account temporarily blocked. Please try again in {minutes}m {seconds}s")
        
        # Check OTP rate limit for login
        can_request, attempts_remaining = check_otp_limit(sync_redis, login_data.email, "login")
        
        if not can_request:
            # Block user for 24 hours (86400 seconds)
            sync_redis.setex(block_key, 86400, "blocked")
            raise ValueError("Login limit exceeded. Account blocked for 24 hours.")
        
        # Generate and send OTP
        otp = generate_otp()
        otp_key = f"otp:login:{login_data.email}"
        sync_redis.set(otp_key, otp, ex=300)  # 5 minutes expiry
        increment_otp_count(sync_redis, login_data.email, "login")
        send_otp_email(login_data.email, otp)
        
        return {
            "message": "Login OTP sent successfully",
            "attempts_remaining": attempts_remaining - 1
        }
    
    @staticmethod
    def forget_password(forget_data: ForgetPassword) -> Dict[str, Any]:
        """Send OTP for password reset"""
        # Check if user exists
        user = User.query.filter_by(email=forget_data.email).first()
        if not user:
            raise ValueError("User not found")
        
        # Check OTP rate limit for password reset
        sync_redis = get_sync_redis()
        can_request, attempts_remaining = check_otp_limit(sync_redis, forget_data.email, "forgetpassword")
        
        if not can_request:
            remaining_time = get_otp_remaining_time(sync_redis, forget_data.email, "forgetpassword")
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            raise ValueError(f"OTP limit exceeded. Please try again in {hours}h {minutes}m")
        
        # Generate and send OTP
        otp = generate_otp()
        otp_key = f"otp:forgetpassword:{forget_data.email}"
        sync_redis.set(otp_key, otp, ex=300)
        increment_otp_count(sync_redis, forget_data.email, "forgetpassword")
        send_otp_email(forget_data.email, otp)
        
        return {
            "message": "Password reset OTP sent successfully",
            "attempts_remaining": attempts_remaining - 1
        }
    
    @staticmethod
    def reset_password(reset_data: ResetPassword) -> Dict[str, Any]:
        """Reset password using OTP"""
        # Find user
        user = User.query.filter_by(email=reset_data.email, is_active=True).first()
        if not user:
            raise ValueError("User not found")
        
        # Get OTP from Redis
        sync_redis = get_sync_redis()
        if not sync_redis:
            raise ValueError("Redis connection failed")
        
        # Use module-based keys
        module = getattr(reset_data, 'module', 'forgetpassword')
        
        # Check if user is blocked due to wrong OTP attempts
        otp_block_key = f"blocked_user:{module}:{reset_data.email}"
        is_otp_blocked = sync_redis.get(otp_block_key)
        
        if is_otp_blocked:
            remaining_block_time = sync_redis.ttl(otp_block_key)
            minutes = remaining_block_time // 60
            seconds = remaining_block_time % 60
            raise ValueError(f"Account blocked due to multiple wrong OTP attempts. Please try again in {minutes}m {seconds}s")
        
        # Get OTP from Redis using module-based key
        otp_key = f"otp:{module}:{reset_data.email}"
        stored_otp = sync_redis.get(otp_key)
        if stored_otp is None or stored_otp.decode('utf-8') != reset_data.code:
            # Increment wrong OTP attempt count using module-based key
            wrong_attempt_key = f"wrong_otp_attempts:{reset_data.email}:{module}"
            current_attempts = sync_redis.get(wrong_attempt_key)
            
            if current_attempts is None:
                # First wrong attempt
                sync_redis.setex(wrong_attempt_key, 3600, 1)  # 1 hour window
            else:
                attempts = int(current_attempts) + 1
                if attempts >= 5:  # Block after 5 wrong attempts
                    # Block user for 30 minutes (1800 seconds)
                    sync_redis.setex(otp_block_key, 1800, "blocked")
                    sync_redis.delete(wrong_attempt_key)
                    raise ValueError("Account blocked due to multiple wrong OTP attempts. Please try again in 30 minutes.")
                else:
                    sync_redis.incr(wrong_attempt_key)
            
            raise ValueError("Invalid OTP")
        
        # OTP is correct - reset wrong attempt counter and proceed
        sync_redis.delete(f"wrong_otp_attempts:{reset_data.email}:{module}")
        
        # Update password and delete OTP from Redis
        user.password_hash = bcrypt.hash(reset_data.new_password)
        db.session.commit()
        sync_redis.delete(otp_key)
        reset_otp_limit(sync_redis, reset_data.email, module)
        
        # Unblock user if they were blocked
        sync_redis.delete(otp_block_key)
        
        return {"message": "Password reset successfully"}
    
    @staticmethod
    def get_current_user(user_id: str) -> Optional[User]:
        """Get current user by ID"""
        return User.query.get(user_id) 