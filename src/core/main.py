import os, hashlib, secrets
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from src.models import models, schemas
from src.data.database import engine, get_db, SessionLocal

def init_db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(models.User).filter_by(username="admin").first():
            db.add(models.User(
                username="admin",
                password=hashlib.sha256(b"admin123").hexdigest(),
                full_name="Sistem Yöneticisi", role="admin"
            ))
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="PersonelPro API", lifespan=lifespan)
app.add_middleware(CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"])

sessions = {}  # token -> username

def hp(pw): return hashlib.sha256(pw.encode()).hexdigest()

def auth(token: str = Query(None), db: Session = Depends(get_db)):
    if not token or token not in sessions:
        raise HTTPException(401, "Oturum geçersiz")
    u = db.query(models.User).filter_by(username=sessions[token]).first()
    if not u: raise HTTPException(401, "Kullanıcı bulunamadı")
    return u

FRONT = os.path.join(os.path.dirname(__file__), "..", "ui", "index.html")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    if os.path.exists(FRONT):
        return HTMLResponse(open(FRONT, encoding="utf-8").read())
    return HTMLResponse("frontend/index.html bulunamadı", 404)

@app.post("/api/login")
def login(p: schemas.LoginRequest, db: Session = Depends(get_db)):
    u = db.query(models.User).filter_by(username=p.username).first()
    if not u or u.password != hp(p.password):
        raise HTTPException(401, "Kullanıcı adı veya şifre hatalı")
    t = secrets.token_urlsafe(32)
    sessions[t] = u.username
    return {"token": t, "username": u.username, "full_name": u.full_name, "role": u.role}

@app.post("/api/logout")
def logout(token: str = Query(...)):
    sessions.pop(token, None)
    return {"ok": True}

@app.get("/api/me")
def me(u=Depends(auth)):
    return {"username": u.username, "full_name": u.full_name, "role": u.role}

@app.get("/api/stats")
def stats(db: Session = Depends(get_db), u=Depends(auth)):
    all_emp = db.query(models.Employee).all()
    total = len(all_emp)
    depts = {}
    for e in all_emp:
        depts[e.department] = depts.get(e.department, 0) + 1
    return {
        "total": total,
        "active": sum(1 for e in all_emp if e.status == "active"),
        "inactive": sum(1 for e in all_emp if e.status == "inactive"),
        "on_leave": sum(1 for e in all_emp if e.status == "on_leave"),
        "avg_salary": round(sum(e.salary for e in all_emp) / total, 2) if total else 0,
        "payroll": round(sum(e.salary for e in all_emp if e.status == "active"), 2),
        "departments": depts,
    }

@app.get("/api/employees")
def list_emp(
    search: Optional[str] = None,
    dept: Optional[str] = None,
    emp_status: Optional[str] = Query(None, alias="emp_status"),
    db: Session = Depends(get_db), u=Depends(auth)
):
    q = db.query(models.Employee)
    if search:
        s = f"%{search}%"
        q = q.filter(or_(
            models.Employee.first_name.ilike(s),
            models.Employee.last_name.ilike(s),
            models.Employee.email.ilike(s),
            models.Employee.position.ilike(s),
        ))
    if dept: q = q.filter(models.Employee.department == dept)
    if emp_status: q = q.filter(models.Employee.status == emp_status)
    return q.order_by(models.Employee.id.desc()).all()

@app.get("/api/employees/{eid}")
def get_emp(eid: int, db: Session = Depends(get_db), u=Depends(auth)):
    e = db.query(models.Employee).get(eid)
    if not e: raise HTTPException(404, "Bulunamadı")
    return e

@app.post("/api/employees", status_code=201)
def add_emp(p: schemas.EmployeeCreate, db: Session = Depends(get_db), u=Depends(auth)):
    if db.query(models.Employee).filter_by(email=p.email).first():
        raise HTTPException(409, "Bu e-posta zaten kayıtlı")
    colors = ["#E63946","#2A9D8F","#F4A261","#7209B7","#3A86FF","#06D6A0","#FB5607","#118AB2"]
    n = db.query(models.Employee).count()
    d = p.model_dump()
    d["avatar_color"] = d.get("avatar_color") or colors[n % len(colors)]
    e = models.Employee(**d)
    db.add(e); db.commit(); db.refresh(e)
    return e

@app.put("/api/employees/{eid}")
def update_emp(eid: int, p: schemas.EmployeeUpdate, db: Session = Depends(get_db), u=Depends(auth)):
    e = db.query(models.Employee).get(eid)
    if not e: raise HTTPException(404, "Bulunamadı")
    for k, v in p.model_dump(exclude_unset=True).items():
        setattr(e, k, v)
    db.commit(); db.refresh(e)
    return e

@app.delete("/api/employees/{eid}", status_code=204)
def del_emp(eid: int, db: Session = Depends(get_db), u=Depends(auth)):
    e = db.query(models.Employee).get(eid)
    if not e: raise HTTPException(404, "Bulunamadı")
    db.delete(e); db.commit()

@app.get("/api/departments")
def get_depts(db: Session = Depends(get_db), u=Depends(auth)):
    rows = db.query(models.Employee.department).distinct().all()
    return [r[0] for r in rows if r[0]]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
