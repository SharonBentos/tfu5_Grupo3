from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.models import EstadoPedido, MetodoPago, RolEmpleado

# ─── PRODUCTO ───────────────────────────────
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    disponible: bool

    class Config:
        from_attributes = True

# ─── DETALLE PEDIDO ───────────────────────────────
class DetallePedidoRequest(BaseModel):
    producto_id: int
    cantidad: int
    observaciones: Optional[str] = None

class DetallePedidoResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    observaciones: Optional[str]

    class Config:
        from_attributes = True

# ─── PEDIDO ───────────────────────────────
class PedidoRequest(BaseModel):
    nombre_cliente: str
    detalles: List[DetallePedidoRequest]

class PedidoResponse(BaseModel):
    id: int
    numero_seguimiento: str
    nombre_cliente: str
    fecha_hora: datetime
    estado: EstadoPedido
    total: float
    detalles: List[DetallePedidoResponse]

    class Config:
        from_attributes = True

# ─── PAGO ───────────────────────────────
class PagoRequest(BaseModel):
    metodo: MetodoPago

class PagoResponse(BaseModel):
    id: int
    pedido_id: int
    monto: float
    metodo: MetodoPago
    exitoso: bool
    referencia_externa: Optional[str]
    mensaje: str

    class Config:
        from_attributes = True

# ─── AUTH ───────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str