# Auth API

## هدف
مدیریت ثبت‌نام، ورود و دریافت توکن برای کاربر.

> در MVP می‌توان احراز هویت را ساده نگه داشت.
> اگر ورود از طریق روبیکا مستقیم در دسترس نیست، می‌توان احراز هویت داخلی داشت.

---

## 1. Register User

### Endpoint
```http
POST /api/v1/auth/register

### Request Body
json
{
  "full_name": "Ali Ahmadi",
  "username": "ali_admin",
  "phone": "09120000000",
  "password": "StrongPass123"
}

### Validation
- `full_name`: required, max 150
- `username`: optional, unique, max 100
- `phone`: required, unique
- `password`: required, min 8

### Response
json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
"user": {
"id": 1,
"full_name": "Ali Ahmadi",
"username": "ali_admin",
"phone": "09120000000",
"role": "customer",
"status": "active"
},
"tokens": {
"access_token": "jwt_access_token",
"refresh_token": "jwt_refresh_token"
}
  }
}

---

## 2. Login

### Endpoint
http
POST /api/v1/auth/login

### Request Body
json
{
  "phone": "09120000000",
  "password": "StrongPass123"
}

### Response
json
{
  "success": true,
  "message": "Login successful",
  "data": {
"user": {
"id": 1,
"full_name": "Ali Ahmadi",
"username": "ali_admin",
"phone": "09120000000",
"role": "customer",
"status": "active"
},
"tokens": {
"access_token": "jwt_access_token",
"refresh_token": "jwt_refresh_token"
}
  }
}

---

## 3. Refresh Token

### Endpoint
http
POST /api/v1/auth/refresh

### Request Body
json
{
  "refresh_token": "jwt_refresh_token"
}

### Response
json
{
  "success": true,
  "message": "Token refreshed",
  "data": {
"access_token": "new_access_token"
  }
}

---

## 4. Get Current User

### Endpoint
http
GET /api/v1/auth/me

### Headers
http
Authorization: Bearer <token>

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"id": 1,
"full_name": "Ali Ahmadi",
"username": "ali_admin",
"phone": "09120000000",
"role": "customer",
"status": "active"
  }
}

---

## 5. Logout

### Endpoint
http
POST /api/v1/auth/logout

### Request Body
json
{
  "refresh_token": "jwt_refresh_token"
}

### Response
json
{
  "success": true,
  "message": "Logged out successfully",
  "data": null
}

---

## خطاهای رایج
- `PHONE_ALREADY_EXISTS`
- `INVALID_CREDENTIALS`
- `USER_BLOCKED`
- `INVALID_REFRESH_TOKEN`

