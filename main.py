import os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parent
DB=os.getenv("DATABASE_PATH",str(ROOT/"events.db"))
KEY=os.getenv("EVENT_API_KEY","")
app=FastAPI(title="Hasta İzleme Sunucusu",version="1.0.0")
app.mount("/static",StaticFiles(directory=ROOT/"static"),name="static")

class Event(BaseModel):
    room_id:str=Field(min_length=1,max_length=50)
    event_type:str=Field(min_length=1,max_length=80)
    risk_level:str="bilgi"
    message:str=""
    source:str="spyder"
    timestamp:Optional[str]=None

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
with db() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,room_id TEXT,event_type TEXT,risk_level TEXT,message TEXT,source TEXT,timestamp TEXT,received_at TEXT)""")

clients=set()
@app.get("/")
def home(): return FileResponse(ROOT/"static"/"index.html")
@app.get("/health")
def health(): return {"status":"ok","service":"hasta-izleme-sunucusu"}
@app.get("/api/events")
def get_events(limit:int=100):
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?",(max(1,min(limit,500)),))]
@app.post("/api/events")
async def post_event(e:Event,x_api_key:Optional[str]=Header(default=None)):
    if KEY and x_api_key!=KEY: raise HTTPException(401,"Geçersiz API anahtarı")
    received=datetime.now(timezone.utc).isoformat()
    with db() as c:
        cur=c.execute("INSERT INTO events(room_id,event_type,risk_level,message,source,timestamp,received_at) VALUES(?,?,?,?,?,?,?)",(e.room_id,e.event_type,e.risk_level,e.message,e.source,e.timestamp,received))
        item={"id":cur.lastrowid,**e.model_dump(),"received_at":received}
    dead=[]
    for ws in list(clients):
        try: await ws.send_json({"kind":"new_event","event":item})
        except Exception: dead.append(ws)
    for ws in dead: clients.discard(ws)
    return item
@app.websocket("/ws")
async def socket(ws:WebSocket):
    await ws.accept(); clients.add(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: clients.discard(ws)
