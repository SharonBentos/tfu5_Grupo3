from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# Patrón STATE: estados del pedido
class EstadoPedido(str, enum.Enum):
    REGISTRADO = "REGISTRADO"
    PAGADO = "PAGADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    RETIRADO = "RETIRADO"
    CANCELADO = "CANCELADO"

# Patrón STRATEGY: métodos de pago
class MetodoPago(str, enum.Enum):
    EFECTIVO = "EFECTIVO"
    TARJETA = "TARJETA"

class RolEmpleado(str, enum.Enum):
    CAJERO = "CAJERO"
    COCINERO = "COCINERO"
    ADMIN = "ADMIN"

# Patrón ENTITY: empleado con identidad propia
class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    rol = Column(Enum(RolEmpleado), nullable=False)

# Patrón ENTITY: producto del menú
class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    disponible = Column(Boolean, default=True)

# Patrón AGGREGATE: Pedido es la raíz, contiene los detalles
class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero_seguimiento = Column(String(20), unique=True)
    nombre_cliente = Column(String(100), nullable=False)
    fecha_hora = Column(DateTime, default=datetime.now)
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.REGISTRADO)
    total = Column(Float, default=0.0)
    empleado_id = Column(Integer, ForeignKey("empleados.id"))

    empleado = relationship("Empleado")
    detalles = relationship("DetallePedido", back_populates="pedido")

# Patrón ENTITY: línea del pedido
class DetallePedido(Base):
    __tablename__ = "detalles_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    observaciones = Column(String(255))

    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto")

    def calcular_subtotal(self):
        return self.precio_unitario * self.cantidad

# Patrón ENTITY: transacción de pago
class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    monto = Column(Float, nullable=False)
    metodo = Column(Enum(MetodoPago), nullable=False)
    fecha_hora = Column(DateTime, default=datetime.now)
    referencia_externa = Column(String(100))
    exitoso = Column(Boolean, default=False)

    pedido = relationship("Pedido")