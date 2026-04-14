from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import time


from .auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, timedelta, FAKE_USERS_DB
from .database import init_db, get_db, QueryLog
import sys
import os

# Add parent directory to sys.path to allow importing from model
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model.ensemble import SQLiEnsemblePredictor
from model.validation import StructuralIntegrityCheck

# Rate Limiting (Simple in-memory cache for college demo)
# In production, use Redis/SlowAPI
request_history: Dict[str, float] = {}
RATE_LIMIT_SECONDS = 1.0  # Allow 1 request per second per IP
MAX_PAYLOAD_SIZE = 2048   # Reject queries > 2KB

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Semantic-Aware SQL Injection Detection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = None
sic = StructuralIntegrityCheck() # Single global instance for high performance

@app.on_event("startup")
def startup_event():
    global predictor
    init_db()
    try:
        predictor = SQLiEnsemblePredictor()
    except Exception as e:
        print(f"Warning: Predictor failed to load on startup. {e}")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


class QueryRequest(BaseModel):
    query: str
    source_ip: str = "192.168.1.105"
    endpoint: str = "/login"

class QueryResponse(BaseModel):
    prediction: int
    confidence: float
    risk_level: str
    individual_probabilities: Dict[str, float]
    attack_type: str = "Normal"
    keywords: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str

# authenticate_user is now imported from .auth

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predict", response_model=QueryResponse)
async def predict_query(req: QueryRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 1. API Protection: Rate Limiting
    now = time.time()
    last_req = request_history.get(req.source_ip, 0)
    if now - last_req < RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail="Too many requests. Rate limit active for security.")
    request_history[req.source_ip] = now

    # 2. API Protection: Payload size capping
    if len(req.query) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large. Potential Denial of Service attempt.")

    if not predictor:
        raise HTTPException(status_code=500, detail="Model predictor not initialized.")
    
    # 3. Security Hardening: Structural Integrity Check (SIC)
    start_time = time.time()
    sic_result = sic.validate(req.query)
    
    # Pre-inference block if SIC finds high risk (Fast Fail)
    if sic_result["is_high_risk"]:
        result = {
            "prediction": 1,
            "confidence": 1.0,
            "risk_level": "High (Auto-Block)",
            "individual_probabilities": {"SIC_Sensor": 1.0},
            "attack_type": f"Heuristic Block: {sic_result['reasons'][0]}",
            "keywords": sic_result["reasons"]
        }
    else:
        # Proceed to AI Ensemble but pass reasons as insights if any
        result = predictor.predict(req.query)
        if sic_result["reasons"]:
             result["keywords"].extend(sic_result["reasons"])
             result["risk_level"] = "High" # Escalate if SIC had minor concerns
    
    # Check if we should block (simulate WAF rule)
    blocked = result["prediction"] == 1
    
    # Log to database
    log_entry = QueryLog(
        query=req.query,
        prediction=result["prediction"],
        confidence=result["confidence"],
        risk_level=result["risk_level"],
        blocked=blocked,
        source_ip=req.source_ip,
        endpoint=req.endpoint,
        attack_type=result.get("attack_type", "Normal")
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    # Broadcast to websocket
    alert_data = {
        "timestamp": log_entry.timestamp.strftime('%H:%M:%S'),
        "source_ip": log_entry.source_ip,
        "endpoint": log_entry.endpoint,
        "prediction": log_entry.prediction,
        "confidence": log_entry.confidence,
        "risk_level": log_entry.risk_level,
        "attack_type": log_entry.attack_type,
        "query": log_entry.query
    }
    await manager.broadcast(json.dumps(alert_data))
    
    inference_time = (time.time() - start_time) * 1000
    print(f"DEBUG: Inference complete in {inference_time:.2f}ms | Verdict: {result['risk_level']}")
    
    return result

@app.get("/logs")
def get_logs(limit: int = 100, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    logs = db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()
    return logs
