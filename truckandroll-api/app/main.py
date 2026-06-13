from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.database import engine, Base
from app.routers import auth, productos, pedidos, pagos
from app.models import models
from app.models.models import Empleado, RolEmpleado
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Crea todas las tablas en la base de datos al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Truck & Roll API", version="1.0.0")

# Redirige la raíz a /docs automáticamente
@app.get("/")
def root():
    return RedirectResponse(url="/docs")

# Registra los routers (endpoints)
app.include_router(auth.router)
app.include_router(productos.router)
app.include_router(pedidos.router)
app.include_router(pagos.router)

# Carga datos de prueba al iniciar
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def cargar_datos_iniciales():
    db = Session(engine)
    
    if db.query(Empleado).count() == 0:
        empleados = [
            Empleado(nombre="Juan Cajero", username="cajero1", 
                    password=pwd_context.hash("cajero123"), rol=RolEmpleado.CAJERO),
            Empleado(nombre="Pedro Cocinero", username="cocinero1",
                    password=pwd_context.hash("cocinero123"), rol=RolEmpleado.COCINERO),
            Empleado(nombre="Admin", username="admin",
                    password=pwd_context.hash("admin123"), rol=RolEmpleado.ADMIN),
        ]
        db.add_all(empleados)
        db.commit()

    from app.models.models import Producto
    if db.query(Producto).count() == 0:
        productos = [
            Producto(nombre="Hamburguesa Clásica", descripcion="Carne, lechuga y tomate", precio=350.0),
            Producto(nombre="Hamburguesa Doble", descripcion="Doble carne y bacon", precio=480.0),
            Producto(nombre="Papas Fritas", descripcion="Papas crocantes", precio=150.0),
            Producto(nombre="Bebida", descripcion="Coca, Pepsi o Sprite", precio=80.0),
            Producto(nombre="Agua", descripcion="Agua mineral 500ml", precio=60.0),
            Producto(nombre="Wrap de Pollo", descripcion="Pollo grillado y lechuga", precio=320.0),
        ]
        db.add_all(productos)
        db.commit()
    
    db.close()