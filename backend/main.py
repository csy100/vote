from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from database import get_db, engine
import models

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


class VoteCreate(BaseModel):
    option_id: int
    client_id: str


# 初始化投票数据（如果数据库为空）
def init_poll_data(db: Session):
    poll = db.query(models.Poll).first()
    if not poll:
        poll = models.Poll(question="你最喜欢的编程语言是什么？")
        db.add(poll)
        db.commit()
        db.refresh(poll)

        options = [
            models.Option(poll_id=poll.id, text="Python"),
            models.Option(poll_id=poll.id, text="JavaScript"),
            models.Option(poll_id=poll.id, text="Java"),
            models.Option(poll_id=poll.id, text="Go"),
        ]
        db.bulk_save_objects(options)
        db.commit()


@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    init_poll_data(db)


@app.get("/api/poll")
async def get_poll(db: Session = Depends(get_db)):
    """获取当前问卷和投票统计"""
    poll = db.query(models.Poll).first()
    options = db.query(models.Option).filter(models.Option.poll_id == poll.id).all()

    poll_data = {
        "id": poll.id,
        "question": poll.question,
        "options": [{"id": opt.id, "text": opt.text} for opt in options],
    }

    results = {opt.id: opt.votes_count for opt in options}

    return {"poll": poll_data, "results": results}


@app.post("/api/poll/vote")
async def submit_vote(vote: VoteCreate, db: Session = Depends(get_db)):
    """提交投票"""
    # 检查是否已经投票
    existing_vote = (
        db.query(models.Vote).filter(models.Vote.client_id == vote.client_id).first()
    )

    if existing_vote:
        raise HTTPException(status_code=400, detail="您已经投过票了")

    # 检查选项是否有效
    option = db.query(models.Option).filter(models.Option.id == vote.option_id).first()
    if not option:
        raise HTTPException(status_code=400, detail="无效的选项")

    # 记录投票
    new_vote = models.Vote(option_id=vote.option_id, client_id=vote.client_id)
    db.add(new_vote)

    # 更新选项票数
    option.votes_count += 1

    db.commit()

    # 获取最新结果
    options = db.query(models.Option).all()
    results = {opt.id: opt.votes_count for opt in options}

    # 广播更新后的结果给所有WebSocket连接
    await manager.broadcast(json.dumps({"type": "vote_update", "results": results}))

    return {"success": True, "results": results}


@app.websocket("/ws/poll")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 等待客户端消息（保持连接活跃）
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
