# src/core/task_broker.py
from typing import Dict, Any, Optional
from funboost import BoostersManager
import logging

logger = logging.getLogger(__name__)

class TaskBroker:
    def __init__(self):
        self.boosters_manager = BoostersManager()
    
    def start_all_consumers(self):
        """启动所有任务的消费者"""
        try:
            self.boosters_manager.consume_all()
            logger.info("所有任务消费者已启动")
        except Exception as e:
            logger.error(f"启动任务消费者失败: {e}")
            raise
    
    def stop_all_consumers(self):
        """停止所有任务的消费者"""
        try:
            self.boosters_manager.stop_all()
            logger.info("所有任务消费者已停止")
        except Exception as e:
            logger.error(f"停止任务消费者失败: {e}")
            raise
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取所有队列的状态信息"""
        status = {}
        for booster in self.boosters_manager.get_all_booster_dict().values():
            queue_name = booster.queue_name
            publisher = booster.publisher
            status[queue_name] = {
                "queue_name": queue_name,
                "message_count": publisher.get_message_count(),
                "pending_tasks": publisher.get_message_count()
            }
        return status

# 全局任务代理实例
task_broker = TaskBroker()
