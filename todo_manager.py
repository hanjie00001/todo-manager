#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人待办事项管理器 (Personal Todo Manager)

功能:
  - 添加待办事项（内容、优先级、截止日期）
  - 查看待办事项列表（按优先级或截止日期排序）
  - 标记待办事项为已完成
  - 删除已完成的待办事项
  - 按状态筛选（全部 / 未完成 / 已完成）

数据以JSON格式持久化存储在本地文件中。
"""

import json
import os
from datetime import datetime, date

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


class TodoItem:
    """表示单个待办事项。"""

    PRIORITY_MAP = {"高": 3, "中": 2, "低": 1}
    PRIORITY_NAMES = {3: "高", 2: "中", 1: "低"}

    def __init__(self, content, priority="中", due_date=None, completed=False, created_at=None, todo_id=None):
        self.id = todo_id or self._next_id()
        self.content = content
        self.priority = self.PRIORITY_MAP.get(priority, 2)  # 默认中优先级
        self.due_date = due_date  # 格式: "YYYY-MM-DD" 或 None
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _next_id():
        """生成一个新的ID（基于当前时间戳）。"""
        return int(datetime.now().timestamp() * 1000)

    def to_dict(self):
        """转换为可序列化的字典。"""
        return {
            "id": self.id,
            "content": self.content,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """从字典恢复对象。"""
        item = cls(
            content=data["content"],
            priority=cls.PRIORITY_NAMES.get(data["priority"], "中"),
            due_date=data.get("due_date"),
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            todo_id=data.get("id"),
        )
        return item

    def priority_label(self):
        """返回优先级中文标签。"""
        return self.PRIORITY_NAMES.get(self.priority, "中")

    def due_str(self):
        """返回截止日期显示字符串。"""
        if not self.due_date:
            return "无截止日期"
        today = date.today()
        try:
            d = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            delta = (d - today).days
            if delta < 0:
                return f"{self.due_date} (已过期{-delta}天)"
            elif delta == 0:
                return f"{self.due_date} (今天截止)"
            elif delta == 1:
                return f"{self.due_date} (明天截止)"
            else:
                return f"{self.due_date} (还剩{delta}天)"
        except ValueError:
            return self.due_date

    def __str__(self):
        status = "✓" if self.completed else "▢"
        return f"[{status}] #{self.id} [{self.priority_label()}] {self.content} | {self.due_str()}"

    def short_str(self):
        status = "✓" if self.completed else "▢"
        return f"{status} #{self.id} {self.content[:30]}{'...' if len(self.content) > 30 else ''}"
