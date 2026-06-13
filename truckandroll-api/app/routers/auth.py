from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.database import get_db
from app.models.models import Empleado
from app.schemas.schemas import LoginRequest
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Autenticación"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración del token
SECRET_KEY = "truckandroll2026secretkey"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Genera el token JWT
def crear_token(data: dict):
    datos = data.copy()
    expira = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    datos.update({"exp": expira})
    return jwt.encode(datos, SECRET_KEY, algorithm=ALGORITHM)

# Verifica el token y retorna el empleado
def get_empleado_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    empleado = db.query(Empleado).filter(Empleado.username == username).first()
    if not empleado:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return empleado

# RF-001: POST /auth/login
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    empleado = db.query(Empleado).filter(Empleado.username == request.username).first()
    
    if not empleado:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    if not pwd_context.verify(request.password, empleado.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    token = crear_token({"sub": empleado.username})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "nombre": empleado.nombre,
        "rol": empleado.rol
    }