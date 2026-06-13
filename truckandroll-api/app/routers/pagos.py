from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Pago, Pedido, EstadoPedido, MetodoPago
from app.schemas.schemas import PagoRequest, PagoResponse
from app.models.models import Empleado
from app.routers.auth import get_empleado_actual
import uuid

router = APIRouter(prefix="/pagos", tags=["Pagos"])

# Patrón ADAPTER: simula la pasarela de pagos externa
def procesar_pasarela(monto: float) -> str:
    import random
    if random.random() > 0.1:
        return "TXN-" + str(uuid.uuid4())[:8].upper()
    raise HTTPException(status_code=402, detail="Pago rechazado por la pasarela")

# Patrón STRATEGY: selecciona cómo procesar según el método de pago
def procesar_pago_strategy(metodo: MetodoPago, monto: float):
    if metodo == MetodoPago.EFECTIVO:
        # Efectivo: se registra internamente sin pasarela
        return None, True, "Pago en efectivo registrado correctamente"
    else:
        # Tarjeta: consulta la pasarela externa
        referencia = procesar_pasarela(monto)
        return referencia, True, "Pago con tarjeta aprobado"

# RF-003: POST /pagos/{pedido_id} — procesar pago
@router.post("/{pedido_id}", response_model=PagoResponse)
def procesar_pago(pedido_id: int, request: PagoRequest, db: Session = Depends(get_db), empleado: Empleado = Depends(get_empleado_actual)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != EstadoPedido.REGISTRADO:
        raise HTTPException(status_code=400, detail="El pedido no está en estado válido para pagar")

    referencia, exitoso, mensaje = procesar_pago_strategy(request.metodo, pedido.total)

    pago = Pago(
        pedido_id=pedido.id,
        monto=pedido.total,
        metodo=request.metodo,
        referencia_externa=referencia,
        exitoso=exitoso
    )
    db.add(pago)

    # Patrón STATE: cambia el estado del pedido a PAGADO
    pedido.estado = EstadoPedido.PAGADO
    db.commit()
    db.refresh(pago)

    return PagoResponse(
        id=pago.id,
        pedido_id=pedido.id,
        monto=pago.monto,
        metodo=pago.metodo,
        exitoso=pago.exitoso,
        referencia_externa=pago.referencia_externa,
        mensaje=mensaje
    )