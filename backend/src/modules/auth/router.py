# src/modules/auth/router.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio

from ..auth.tasks import send_email_task, analyze_user_behavior_task, process_batch_data_task
from src.core.task_broker import task_broker

router = APIRouter(prefix="/tasks", tags=["tasks"])

class EmailTaskRequest(BaseModel):
    to_email: str
    subject: str
    content: str

class UserAnalysisRequest(BaseModel):
    user_id: int
    action: str
    timestamp: str

class BatchDataRequest(BaseModel):
    data_batch: List[Any]
    processor_type: str

@router.post("/send-email")
async def create_email_task(request: EmailTaskRequest):
    """创建发送邮件任务"""
    try:
        # 异步推送任务到消息队列
        async_result = send_email_task.push(request.to_email, request.subject, request.content)
        return {
            "message": "邮件任务已提交",
            "task_id": async_result.task_id,
            "queue": "email_send_queue"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")

@router.post("/analyze-user")
async def create_user_analysis_task(request: UserAnalysisRequest):
    """创建用户行为分析任务"""
    try:
        async_result = analyze_user_behavior_task.push(
            request.user_id, request.action, request.timestamp
        )
        return {
            "message": "用户分析任务已提交",
            "task_id": async_result.task_id,
            "queue": "user_analysis_queue"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")

@router.post("/process-batch-data")
async def create_batch_data_task(request: BatchDataRequest):
    """创建批量数据处理任务"""
    try:
        async_result = process_batch_data_task.push(
            request.data_batch, request.processor_type
        )
        return {
            "message": "批量数据处理任务已提交",
            "task_id": async_result.task_id,
            "queue": "data_processing_queue",
            "data_count": len(request.data_batch)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务提交失败: {str(e)}")

@router.get("/queue-status")
async def get_queue_status():
    """获取所有队列状态"""
    try:
        status = task_broker.get_queue_status()
        return {"queues": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取队列状态失败: {str(e)}")

@router.post("/start-consumers")
async def start_consumers():
    """启动所有任务消费者"""
    try:
        # 在后台线程中启动消费者
        import threading
        def start_consumers_thread():
            task_broker.start_all_consumers()
        
        thread = threading.Thread(target=start_consumers_thread, daemon=True)
        thread.start()
        
        return {"message": "任务消费者启动命令已发送"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动消费者失败: {str(e)}")

@router.get("/task-result/{task_id}")
async def get_task_result(task_id: str):
    """获取任务执行结果（如果使用RPC模式）"""
    # 注意：需要设置is_using_rpc_mode=True才能使用此功能
    try:
        # 这里需要根据具体的任务ID查询结果
        # 实际实现可能需要连接Redis查询结果
        return {"message": "获取任务结果功能需要配置RPC模式"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")
