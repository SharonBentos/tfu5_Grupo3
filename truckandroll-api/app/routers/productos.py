from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Producto, RolEmpleado
from app.schemas.schemas import ProductoResponse
from app.models.models import Empleado
from app.routers.auth import get_empleado_actual

router = APIRouter(prefix="/productos", tags=["Productos"])

# GET /productos — lista productos disponibles (para el cajero al registrar pedido)
@router.get("/disponibles", response_model=list[ProductoResponse])
def listar_productos(db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    return db.query(Producto).filter(Producto.disponible == True).all()

# GET /productos/todos — lista todos (para administración)
@router.get("/todos", response_model=list[ProductoResponse])
def listar_todos(db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    return db.query(Producto).all()

# POST /productos — crear producto
@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: ProductoResponse, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    if empleado.rol != RolEmpleado.ADMIN:
        raise HTTPException(status_code=403, detail="Solo ADMIN puede crear productos")

    nuevo = Producto(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        disponible=producto.disponible
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# PATCH /productos/{id}/disponibilidad — activar/desactivar producto
@router.patch("/{id}/disponibilidad", response_model=ProductoResponse)
def toggle_disponibilidad(id: int, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.disponible = not producto.disponible
    db.commit()
    db.refresh(producto)
    return producto

# DELETE /productos/{id} — eliminar producto (solo ADMIN)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(id: int, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    if empleado.rol != RolEmpleado.ADMIN:
        raise HTTPException(status_code=403, detail="Solo ADMIN puede eliminar productos")

    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)