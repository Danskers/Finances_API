# Finanzas Media - README.md

### Este proyecto es una aplicación web personal para el control de finanzas, con registro de ingresos, gastos y deudas, gestión de cuentas, subida de facturas (imágenes) a Supabase Storage y visualización de las mismas.
## Descripción general

**Finanzas_API** es una aplicación full-stack desarrollada con:

- **Backend**: FastAPI (Python)
- **Base de datos**: SQLite local (con SQLModel)
- **Almacenamiento de archivos**: Supabase Storage (bucket `facturas`)
- **Frontend**: Jinja2 templates + CSS personalizado
- **Autenticación**: Sesiones con cookies + hashing de contraseñas
- **Despliegue**: https://finances-api-yo11.onrender.com/

La app permite al usuario registrarse, iniciar sesión y gestionar sus finanzas de forma simple y visual.

## Funcionalidades principales

- Registro e inicio de sesión de usuarios
- Gestión de cuentas bancarias/personales
- Registro de transacciones (ingresos, gastos y deudas)
- Clasificación de gastos: fijos/variables con subcategorías
- Subida opcional de facturas (imágenes) almacenadas en Supabase
- Visualización de transacciones por mes
- Búsqueda de transacciones
- Botón "Consultar facturas adjuntas" que muestra una lista con enlaces directos a todas las facturas subidas
- Eliminación de transacciones
- Dashboard con resumen básico

### Modelo de datos

El modelo de datos está definido con **SQLModel** y se almacena en una base de datos SQLite. Consta de tres entidades principales:

#### 1. Usuario
Representa al usuario registrado en la aplicación.


```text
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    nombre: str

    transacciones: List["Transaccion"] = Relationship(back_populates="usuario")
    cuentas: List["Cuenta"] = Relationship(back_populates="usuario")
```
#### 2. Cuenta
Representa las cuentas o fuentes de dinero del usuario (ej. "Cuenta principal", "Efectivo").

```text
class Cuenta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    usuario_id: int = Field(foreign_key="usuario.id")

    usuario: Usuario = Relationship(back_populates="cuentas")
    transacciones: List["Transaccion"] = Relationship(back_populates="cuenta")
```

#### 3. Transaccion
Representa cada movimiento financiero (ingreso, gasto o deuda).

```text
class Transaccion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    monto: float
    tipo: str  # "ingreso", "gasto" o "deuda"
    categoria: str  # "fijo" o "variable"
    subcategoria: Optional[str] = None
    fecha: datetime = Field(default_factory=datetime.utcnow)
    mes: str = Field(default="")  # Formato "YYYY-MM"

    usuario_id: int = Field(foreign_key="usuario.id")
    cuenta_id: int = Field(foreign_key="cuenta.id")

    # URL pública de la factura subida a Supabase Storage (opcional)
    factura_url: Optional[str] = None

    usuario: Usuario = Relationship(back_populates="transacciones")
    cuenta: Cuenta = Relationship(back_populates="transacciones")

```

--- 

### Diagrama de clases (entidades principales)

```text
Usuario
├── id (PK)
├── email
├── hashed_password
├── nombre
└── transacciones (relación 1:N)
    └── cuentas (relación 1:N)

Cuenta
├── id (PK)
├── nombre
├── usuario_id (FK → Usuario.id)
└── transacciones (relación 1:N)

Transaccion
├── id (PK)
├── monto
├── tipo (ingreso/gasto/deuda)
├── categoria (fijo/variable)
├── subcategoria (opcional)
├── fecha (datetime)
├── mes (YYYY-MM)
├── usuario_id (FK → Usuario.id)
├── cuenta_id (FK → Cuenta.id)
└── factura_url (URL pública de la factura en Supabase Storage, opcional)

```

---

Relaciones

Un Usuario tiene muchas Transacciones y muchas Cuentas
Una Cuenta pertenece a un Usuario y tiene muchas Transacciones
Una Transacción pertenece a un Usuario y a una Cuenta



---

### Mapa de Endpoints

```text

Método,Ruta,Descripción,Autenticación
GET,/,Dashboard principal
GET,/register,Formulario de registro
POST,/register,Procesar registro
GET,/login,Formulario de login
POST,/login,Procesar login
GET,/logout,Cerrar sesión
GET,/cuentas,Listado y creación de cuentas
POST,/cuentas,Crear nueva cuenta
POST,/cuenta/eliminar/{id},Eliminar cuenta
GET,/transacciones,Lista de transacciones del mes + formulario de nueva transacción
POST,/transacciones,Crear nueva transacción (con subida opcional de factura)
POST,/transaccion/eliminar/{id},Eliminar transacción
GET,/historial,Historial mensual de transacciones

```

---

Flujo de actividades principal

```text
Registro/Login
El usuario se registra o inicia sesión. Se crea una cookie de sesión segura.
Gestión de cuentas
El usuario crea al menos una cuenta (ej. "Cuenta principal").
Agregar transacciones


Selecciona monto, tipo, categoría, cuenta, etc.
Opcionalmente sube una factura (imagen).
La factura se sube a Supabase Storage usando la service_role key (bypassea RLS).
Se guarda la URL pública en el campo factura_url de la transacción.


Consultar transacciones y facturas
En /transacciones se listan las del mes actual.
Si hay transacciones con factura, aparece el botón "Consultar facturas adjuntas".
Al hacer clic, se despliega una lista con fecha, monto, tipo y enlace directo a la factura.


Despliegue
La aplicación está desplegada en https://finances-api-yo11.onrender.com como un Web Service.
Variables de entorno requeridas (en Render)
textSUPABASE_URL = https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY = (service_role key de Supabase - ¡secreta!)
PYTHON_VERSION = 3.13 (o la versión que uses)
Configuración en Supabase

Bucket facturas creado con Public bucket = ON
Política de SELECT pública (para leer URLs)
Subida realizada con service_role key desde el backend (bypassea RLS)

Tecnologías utilizadas

FastAPI - Framework backend
SQLModel - ORM y modelos
Jinja2 - Templates HTML
Supabase Storage - Almacenamiento de facturas
SQLite - Base de datos (fácil de migrar a PostgreSQL si se desea)
Render.com - Hosting y despliegue

Futuras mejoras posibles

Gráficos de gastos/ingresos (Chart.js o similar)
Exportar transacciones a CSV/Excel
Categorización automática de gastos
Notificaciones o recordatorios de gastos fijos
Soporte multi-moneda
Migración a PostgreSQL (Supabase DB)

