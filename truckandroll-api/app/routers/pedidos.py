from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Pedido, DetallePedido, Producto, EstadoPedido
from app.schemas.schemas import PedidoRequest, PedidoResponse
from app.models.models import Empleado
from app.routers.auth import get_empleado_actual
import uuid

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

# Patrón FACADE: coordina productos, detalles y estado del pedido
def generar_numero_seguimiento():
    return "TRK-" + str(uuid.uuid4())[:4].upper()

# RF-002: POST /pedidos — registrar nuevo pedido
@router.post("/", response_model=PedidoResponse)
def registrar_pedido(request: PedidoRequest, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    pedido = Pedido(
        nombre_cliente=request.nombre_cliente,
        numero_seguimiento=generar_numero_seguimiento(),
        estado=EstadoPedido.REGISTRADO
    )
    db.add(pedido)
    db.flush()

    total = 0.0
    for detalle_req in request.detalles:
        producto = db.query(Producto).filter(Producto.id == detalle_req.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {detalle_req.producto_id} no encontrado")
        if not producto.disponible:
            raise HTTPException(status_code=400, detail=f"Producto {producto.nombre} no disponible")

        detalle = DetallePedido(
            pedido_id=pedido.id,
            producto_id=producto.id,
            cantidad=detalle_req.cantidad,
            precio_unitario=producto.precio,
            observaciones=detalle_req.observaciones
        )
        db.add(detalle)
        total += producto.precio * detalle_req.cantidad

    pedido.total = total
    db.commit()
    db.refresh(pedido)
    return pedido

# GET /pedidos — listar pedidos activos (no cancelados)
@router.get("/", response_model=list[PedidoResponse])
def listar_pedidos_activos(db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    return db.query(Pedido).filter(Pedido.estado != EstadoPedido.CANCELADO).all()

# GET /pedidos/{identificador} — obtener pedido por ID o número de seguimiento (TRK-XXXX)
@router.get("/{identificador}", response_model=PedidoResponse)
def obtener_pedido(identificador: str, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    pedido = None
    
    # Buscar por número de seguimiento si tiene formato TRK-XXXX
    if identificador.startswith("TRK-"):
        pedido = db.query(Pedido).filter(Pedido.numero_seguimiento == identificador).first()
    else:
        # Intentar buscar por ID (debe ser un número)
        try:
            pedido_id = int(identificador)
            pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        except ValueError:
            pass
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido

# RF-005: PATCH /pedidos/{id}/estado — cambiar estado
@router.patch("/{id}/estado", response_model=PedidoResponse)
def cambiar_estado(id: int, nuevo_estado: EstadoPedido, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    pedido = db.query(Pedido).filter(Pedido.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    # Patrón STATE: transiciones válidas según el estado actual
    transiciones_validas = {
        EstadoPedido.REGISTRADO: [EstadoPedido.PAGADO, EstadoPedido.CANCELADO],
        EstadoPedido.PAGADO: [EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO],
        EstadoPedido.EN_PREPARACION: [EstadoPedido.LISTO, EstadoPedido.CANCELADO],
        EstadoPedido.LISTO: [EstadoPedido.RETIRADO],
        EstadoPedido.RETIRADO: [],
        EstadoPedido.CANCELADO: []
    }

    if nuevo_estado not in transiciones_validas[pedido.estado]:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede cambiar de {pedido.estado} a {nuevo_estado}"
        )

    pedido.estado = nuevo_estado
    db.commit()
    db.refresh(pedido)
    return pedido

# RF-006: GET /pedidos/cocina — pedidos para el cocinero
@router.get("/cocina/ver", response_model=list[PedidoResponse])
def pedidos_cocina(db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    return db.query(Pedido).filter(
        Pedido.estado.in_([EstadoPedido.PAGADO, EstadoPedido.EN_PREPARACION])
    ).all()

# RF-007: GET /pedidos/listos — pantalla de retiro
@router.get("/listos/ver", response_model=list[PedidoResponse])
def pedidos_listos(db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    return db.query(Pedido).filter(Pedido.estado == EstadoPedido.LISTO).all()
