# =============================================================================
# LAB 10: Autenticación JWT + RBAC — orders-service/auth.py
# Taller 4: Backend Avanzado con FastAPI
# =============================================================================

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, User as DBUser

# =============================================================================
# 1. CONFIGURACIÓN DE SEGURIDAD
# =============================================================================

SECRET_KEY: str = os.getenv("JWT_SECRET", "supersecret-fallback-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

# =============================================================================
# 2. CIFRADO Y ESQUEMA OAUTH2
# =============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# =============================================================================
# 3. MODELOS DE DATOS (Pydantic)
# =============================================================================

class Token(BaseModel):
    """Respuesta del endpoint de login con el token JWT generado."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Datos decodificados del payload JWT."""
    email: Optional[str] = None
    role: Optional[str] = "user"


class UserInDB(BaseModel):
    """Representación del usuario tal como se almacena (con hash de contraseña)."""
    email: str
    full_name: str
    role: str = "user"
    hashed_password: str

# =============================================================================
# 4. JERARQUÍA DE ROLES (RBAC)
# =============================================================================

ROLE_LEVELS: dict[str, int] = {
    "user":       1,
    "admin":      2,
    "superadmin": 3,
}

# =============================================================================
# 5. FUNCIONES DE CONTRASEÑA
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra su hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash bcrypt de una contraseña."""
    return pwd_context.hash(password)

# =============================================================================
# 6. CREACIÓN DEL TOKEN JWT
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea y firma un token JWT con los datos proporcionados.

    Args:
        data: Payload que se incluirá en el token (ej: {"sub": email, "role": role}).
        expires_delta: Tiempo de expiración personalizado. Si es None, se usan
                       ACCESS_TOKEN_EXPIRE_MINUTES (60 min) por defecto.

    Returns:
        Token JWT firmado como string.
    """
    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# =============================================================================
# 7. IDENTIFICACIÓN DEL USUARIO ACTUAL
# =============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> DBUser:
    """
    Dependencia de FastAPI que extrae y valida el usuario desde el token JWT.

    - Decodifica el token con la SECRET_KEY.
    - Extrae el campo 'sub' (email) y 'role' del payload.
    - Consulta el usuario en la base de datos PostgreSQL.
    - Lanza HTTP 401 si el token es inválido, expirado o el usuario no existe.

    Returns:
        Instancia del modelo SQLAlchemy DBUser del usuario autenticado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role", "user")

        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email, role=role)

    except JWTError:
        raise credentials_exception

    # Consulta del usuario en la base de datos
    user = db.query(DBUser).filter(DBUser.email == token_data.email).first()

    if user is None:
        raise credentials_exception

    return user

# =============================================================================
# 8. CONTROL DE PERMISOS — RBAC (Role-Based Access Control)
# =============================================================================

def require_role(required_role: str):
    """
    Generador de dependencias RBAC para FastAPI.

    Verifica que el usuario autenticado tenga al menos el nivel de rol requerido.
    La jerarquía es: user (1) < admin (2) < superadmin (3).

    Args:
        required_role: Nombre del rol mínimo necesario ("user", "admin" o "superadmin").

    Returns:
        Función de dependencia FastAPI que valida el rol del usuario.

    Raises:
        HTTP 403 Forbidden si el rol del usuario no alcanza el nivel requerido.

    Uso:
        @app.get("/admin-only")
        def admin_route(current_user = Depends(require_role("admin"))):
            ...
    """
    required_level = ROLE_LEVELS.get(required_role, 1)

    async def role_checker(
        current_user: DBUser = Depends(get_current_user),
    ) -> DBUser:
        # Obtener el rol del usuario — el modelo DBUser tiene columna 'name',
        # pero en este contexto usamos el campo del token (almacenado en payload).
        # Si el modelo DB tiene columna 'role', se usa directamente; si no,
        # se lee desde el token decodificado a través de get_current_user.
        # Aquí intentamos leer el atributo 'role' del modelo, con fallback a "user".
        user_role: str = getattr(current_user, "role", "user") or "user"
        user_level: int = ROLE_LEVELS.get(user_role, 1)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permisos insuficientes. Se requiere rol '{required_role}' "
                    f"(nivel {required_level}), pero el usuario tiene '{user_role}' "
                    f"(nivel {user_level})."
                ),
            )

        return current_user

    return role_checker

