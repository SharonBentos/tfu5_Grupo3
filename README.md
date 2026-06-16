# Truck & Roll — API REST

Sistema de gestión de pedidos para el food truck **Truck & Roll**.  
Backend desarrollado con **Python + FastAPI + SQLite**.

---

## Índice

- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Probar los endpoints](#probar-los-endpoints)
- [Endpoints disponibles](#endpoints-disponibles)
- [Usuarios de prueba](#usuarios-de-prueba)

---

## Requisitos

- Python 3.10 o superior
- Visual Studio Code (recomendado)
- Extensión **REST Client** de VS Code (para probar los endpoints)

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPO>
cd truckandroll-api
```

### 2. Crear y activar el entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install fastapi uvicorn sqlalchemy passlib bcrypt==4.0.1 python-jose[cryptography] python-multipart
```

### 4. Ejecutar la API

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

> **Nota:** Al iniciar, el sistema crea automáticamente el archivo `truckandroll.db` (SQLite) con empleados y productos de prueba.

---

## Probar los endpoints

### Opción A — Archivo `requests.http` (recomendado)

1. Instalar la extensión **REST Client** en VS Code.
2. Abrir el archivo `requests.http` en la raíz del proyecto.
3. Ejecutar el primer bloque (**Login**) haciendo click en "Send Request".
4. Copiar el `access_token` de la respuesta (sin comillas) y pegarlo en la variable `@token` al inicio del archivo.
5. Ejecutar los bloques siguientes en orden, siguiendo el flujo indicado por los comentarios.

> **Importante:** al registrar un pedido nuevo, anotar el `id` que devuelve la respuesta y reemplazar el número en los bloques siguientes (pagos y cambios de estado) por ese id.

### Opción B — Documentación interactiva (Swagger)

1. Con la API corriendo, abrir `http://127.0.0.1:8000/docs` en el navegador.
2. Hacer login con `POST /auth/login` para obtener el token.
3. Click en **"Authorize"** (arriba a la derecha) y pegar las credenciales.
4. Probar cualquier endpoint con "Try it out" → "Execute".

---

## Endpoints disponibles

| Método   | Endpoint                          | Descripción                                                                 | Auth |
|----------|-----------------------------------|-----------------------------------------------------------------------------|------|
| `POST`   | `/auth/login`                     | Iniciar sesión (devuelve token JWT)                                        | No   |
| `GET`    | `/productos/disponibles`          | Listar productos disponibles                                                | Sí   |
| `GET`    | `/productos/todos`                | Listar todos los productos                                                  | Sí   |
| `POST`   | `/productos/`                     | Crear producto. Solo ADMIN                                                  | Sí   |
| `PUT`    | `/productos/{id}`                 | Modificar producto. Solo ADMIN                                              | Sí   |
| `DELETE` | `/productos/{id}`                 | Eliminar producto. Solo ADMIN                                               | Sí   |
| `PATCH`  | `/productos/{id}/disponibilidad`   | Activar o desactivar un producto                                            | Sí   |
| `POST`   | `/pedidos/`                       | Registrar pedido (RF-002)                                                   | Sí   |
| `GET`    | `/pedidos/`                       | Listar pedidos activos                                                       | Sí   |
| `GET`    | `/pedidos/{identificador}`        | Ver pedido por identificador. Puede ser el ID numérico o el número `TRK-XXXX` | Sí   |
| `PUT`    | `/pedidos/{identificador}/editar` | Editar pedido por identificador                                             | Sí   |
| `PATCH`  | `/pedidos/{identificador}/editar` | Editar pedido por identificador                                             | Sí   |
| `PATCH`  | `/pedidos/{identificador}/estado` | Cambiar estado (RF-005) por identificador                                   | Sí   |
| `GET`    | `/pedidos/cocina/ver`             | Pedidos en cocina (RF-006)                                                  | Sí   |
| `GET`    | `/pedidos/listos/ver`             | Pedidos listos para retirar (RF-007)                                        | Sí   |
| `POST`   | `/pagos/{pedido_id}`              | Procesar pago (RF-003)                                                      | Sí   |

En los endpoints de pedidos, `identificador` puede ser el `id` numérico o el número de seguimiento con formato `TRK-XXXX`.

### Estados del pedido y transiciones válidas (RF-005)

REGISTRADO → PAGADO → EN_PREPARACION → LISTO → RETIRADO
        ↓           ↓            ↓
    CANCELADO (desde cualquiera de los tres primeros)

Cualquier otra transición devuelve error `400 Bad Request`.

---

## Usuarios de prueba

Al iniciar la aplicación se crean automáticamente:

| Username   | Contraseña   | Rol      |
|------------|--------------|----------|
| `cajero1`  | `cajero123`  | CAJERO   |
| `cocinero1`| `cocinero123`| COCINERO |
| `admin`    | `admin123`   | ADMIN    |

> **Nota:** actualmente y para que sea fueran mas simples las pruebas al momento de comprobar la funcionalidad de los endpoints cualquier usuario autenticado puede acceder a todos los endpoints, independientemente de su rol. La separación de funciones por rol se gestiona desde el frontend (ver documentación del proyecto para más detalle).

---

## Equipo

**Grupo 3 — Análisis y Diseño de Aplicaciones I — UCU**

- Sharon Bentos
- Valentín Curbelo
- Esteban Durán
- Brian Morat

**Profesores:**
- Washington Salaberry
- Tomás Silva