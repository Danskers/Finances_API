from http.client import HTTPException
from fastapi import FastAPI, Request,UploadFile, File, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import select, Session
from datetime import datetime
from typing import Optional
import math
import locale
import uuid
from supabase import create_client, Client
import os
from .supabase_client import supabase
from .database import crear_db, get_session
from .models import Usuario, Cuenta, Transaccion, LimiteMensual
from .routers import uploads
from .security import get_password_hash, verify_password, crear_token, get_user_from_request

print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY length:", len(os.getenv("SUPABASE_KEY") or "NONE"))

app = FastAPI(title="Finanzas personales - Simplificado")
app.include_router(uploads.router)

#supabase
SUPABASE_URL = "https://fdujitwtuecibozsxytk.supabase.co"
SUPABASE_KEY = "sb_secret_dIPA5z6gkzPG7C7O3Pb_RA_Q80ojOOX"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# crear DB
crear_db()

# templates, static y locale
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
locale.setlocale(locale.LC_ALL, "es_CO.UTF-8")


# ---------- Helpers ----------
def month_for_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m")

def current_month_str() -> str:
    return datetime.utcnow().strftime("%Y-%m")

#define el manejo del dinero en COP
def cop(value):
    try:
        return locale.currency(value, grouping="true")
    except:
        return value
templates.env.filters["cop"] = cop


#Creación base de datos render
@app.on_event("startup")
def startup_event():
    crear_db()


# ---------- Auth ----------
@app.get("/")
def root():
    return RedirectResponse(url="/login")
@app.get("/register")
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Crear cuenta", "error": None})

@app.post("/register")
def register_post(request: Request, email: str = Form(...), password: str = Form(...), session = Depends(get_session)):
    statement = select(Usuario).where(Usuario.email == email)
    existing = session.exec(statement).first()
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "title": "Crear cuenta", "error": "El email ya está registrado"})
    hashed = get_password_hash(password)
    user = Usuario(email=email, hashed_password=hashed)
    session.add(user)
    session.commit()
    session.refresh(user)
    # create a default main account
    main_acc = Cuenta(nombre="Cuenta principal", usuario_id=user.id)
    session.add(main_acc)
    session.commit()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Iniciar sesión", "error": None})

@app.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...), session=Depends(get_session)):
    statement = select(Usuario).where(Usuario.email == email)
    user = session.exec(statement).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "title": "Iniciar sesión", "error": "Credenciales inválidas"})
    token = crear_token({"sub": str(user.id)})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ---------- Dashboard ----------
@app.get("/dashboard")
def dashboard(request: Request, session=Depends(get_session)):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")
    # cuentas y balances
    cuentas = session.exec(select(Cuenta).where(Cuenta.usuario_id == user.id)).all()
    cuentas_info = []
    total_balance = 0.0

    for c in cuentas:
        trans = session.exec(select(Transaccion).where(Transaccion.cuenta_id == c.id)).all()
        balance = sum(t.monto if t.tipo == "ingreso" else -t.monto for t in trans)
        cuentas_info.append({"cuenta": c, "balance": balance})
        total_balance += balance

    # métricas del mes actual
    mes = current_month_str()
    trans_mes = session.exec(select(Transaccion).where(Transaccion.usuario_id == user.id).where(Transaccion.mes == mes)).all()
    total_ingresos = sum(t.monto for t in trans_mes if t.tipo == "ingreso")
    total_gastos = sum(t.monto for t in trans_mes if t.tipo in ("gasto", "deuda"))
    limite = session.exec(select(LimiteMensual).where(LimiteMensual.usuario_id == user.id).where(LimiteMensual.mes == mes)).first()
    monto_limite = limite.monto_limite if limite else 0.0
    disponible = (monto_limite - total_gastos) if monto_limite is not None else None

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard",
        "user": user,
        "cuentas_info": cuentas_info,
        "total_balance": total_balance,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "monto_limite": monto_limite,
        "disponible": disponible,
        "mes": mes
    })


# ---------- Cuentas ----------
@app.get("/cuentas")
def cuentas_list(request: Request, session=Depends(get_session)):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")
    cuentas = session.exec(select(Cuenta).where(Cuenta.usuario_id == user.id)).all()
    return templates.TemplateResponse("cuentas.html", {"request": request, "cuentas": cuentas, "user": user})

@app.post("/cuentas")
def cuentas_create(request: Request, nombre: str = Form(...), session=Depends(get_session)):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")
    nueva = Cuenta(nombre=nombre, usuario_id=user.id)
    session.add(nueva)
    session.commit()
    return RedirectResponse(url="/cuentas", status_code=302)

@app.post("/cuentas/editar/{cuenta_id}")
def cuentas_editar(
    request: Request,
    cuenta_id: int,
    nombre: str = Form(...),
    session=Depends(get_session)
):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")

    cuenta = session.exec(
        select(Cuenta).where(Cuenta.id == cuenta_id, Cuenta.usuario_id == user.id)
    ).first()

    if not cuenta:
        return RedirectResponse(url="/cuentas")

    cuenta.nombre = nombre
    session.add(cuenta)
    session.commit()

    return RedirectResponse(url="/cuentas", status_code=302)


@app.post("/cuentas/eliminar/{cuenta_id}")
def eliminar_cuenta(cuenta_id: int, request: Request, session=Depends(get_session)):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")

    cuenta = session.exec(
        select(Cuenta).where(Cuenta.id == cuenta_id, Cuenta.usuario_id == user.id)
    ).first()

    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    # Bloqueo: no permitir eliminar si tiene transacciones
    trans = session.exec(
        select(Transaccion).where(Transaccion.cuenta_id == cuenta.id)
    ).all()

    if trans:
        raise HTTPException(status_code=400, detail="No se puede eliminar una cuenta con transacciones")

    session.delete(cuenta)
    session.commit()

    return RedirectResponse(url="/cuentas", status_code=302)



# ---------- Transacciones ----------
@app.get("/transacciones")
def transacciones_list(
    request: Request,
    session=Depends(get_session),
    mes: Optional[str] = None,
    q: Optional[str] = None
):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")

    mes_q = mes or current_month_str()

    trans = session.exec(
        select(Transaccion)
        .where(Transaccion.usuario_id == user.id)
        .where(Transaccion.mes == mes_q)
        .order_by(Transaccion.fecha.desc())
    ).all()

    # FILTRO DEL BUSCADOR
    if q:
        q_lower = q.lower()
        trans = [
            t for t in trans
            if q_lower in t.categoria.lower()
            or (t.subcategoria and q_lower in t.subcategoria.lower())
            or q_lower in t.tipo.lower()
            or q_lower in str(t.monto)
            or q_lower in t.fecha.strftime("%Y-%m-%d")
        ]

    cuentas = session.exec(select(Cuenta).where(Cuenta.usuario_id == user.id)).all()

    return templates.TemplateResponse(
        "transacciones.html",
        {
            "request": request,
            "transacciones": trans,
            "cuentas": cuentas,
            "user": user,
            "mes": mes_q,
            "q": q or ""
        }
    )


@app.post("/transacciones")
def agregar_transaccion(
    monto: float = Form(...),
    tipo: str = Form(...),
    categoria: str = Form(...),
    subcategoria: str = Form(None),
    cuenta_id: int = Form(...),
    factura: UploadFile = File(None),
    user: Usuario = Depends(get_user_from_request),
    session: Session = Depends(get_session)
):
    if user is None:
        return RedirectResponse("/login", status_code=303)

    mes = datetime.utcnow().strftime("%Y-%m")

    url_imagen = None

    if factura:
        extension = factura.filename.split(".")[-1]
        file_name = f"{user.id}_{uuid.uuid4()}.{extension}"

        supabase.storage.from_("facturas").upload(
            file_name,
            factura.file,
            file_options={"content-type": factura.content_type}
        )

        url_imagen = (
            supabase.storage
            .from_("facturas")
            .get_public_url(file_name)
        )

    nueva = Transaccion(
        monto=monto,
        tipo=tipo,
        categoria=categoria,
        subcategoria=subcategoria,
        cuenta_id=cuenta_id,
        usuario_id=user.id,
        mes=mes,
        url_imagen=url_imagen
    )

    session.add(nueva)
    session.commit()
    session.refresh(nueva)

    return RedirectResponse("/transacciones", status_code=303)



@app.post("/transaccion/eliminar/{tx_id}")
def eliminar_transaccion(
    tx_id: int,
    request: Request,
    session = Depends(get_session)
):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")

    # Buscar la transacción
    tx = session.exec(
        select(Transaccion)
        .where(Transaccion.id == tx_id)
        .where(Transaccion.usuario_id == user.id)
    ).first()

    if not tx:
        raise HTTPException(404, "Transacción no encontrada")

    session.delete(tx)
    session.commit()

    return RedirectResponse(url="/transacciones", status_code=302)




# ---------- Límite mensual ----------
@app.post("/limite")
def set_limite(request: Request, mes: str = Form(...), monto_limite: float = Form(...), session=Depends(get_session)):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")
    existing = session.exec(select(LimiteMensual).where(LimiteMensual.usuario_id == user.id).where(LimiteMensual.mes == mes)).first()
    if existing:
        existing.monto_limite = monto_limite
        session.add(existing)
    else:
        nuevo = LimiteMensual(usuario_id=user.id, mes=mes, monto_limite=monto_limite)
        session.add(nuevo)
    session.commit()
    return RedirectResponse(url="/dashboard", status_code=302)


# ---------- Historial (mes a mes) ----------
@app.get("/historial")
def historial(request: Request, session=Depends(get_session), mes: Optional[str] = None):
    user = get_user_from_request(request, session)
    if not user:
        return RedirectResponse(url="/login")
    mes_q = mes or current_month_str()
    trans = session.exec(select(Transaccion).where(Transaccion.usuario_id == user.id).where(Transaccion.mes == mes_q).order_by(Transaccion.fecha.desc())).all()
    total_ingresos = sum(t.monto for t in trans if t.tipo == "ingreso")
    total_gastos = sum(t.monto for t in trans if t.tipo in ("gasto", "deuda"))
    limite = session.exec(select(LimiteMensual).where(LimiteMensual.usuario_id == user.id).where(LimiteMensual.mes == mes_q)).first()
    return templates.TemplateResponse("historial.html", {
        "request": request,
        "user": user,
        "transacciones": trans,
        "mes": mes_q,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "monto_limite": limite.monto_limite if limite else 0.0
    })
