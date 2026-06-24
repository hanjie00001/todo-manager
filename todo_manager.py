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


class TodoManager:
    """待办事项管理器，负责数据的增删改查和持久化。"""

    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.items = []  # type: list[TodoItem]
        self._load()

    def _load(self):
        """从JSON文件加载数据。"""
        if not os.path.exists(self.data_file):
            self.items = []
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.items = [TodoItem.from_dict(d) for d in data]
        except (json.JSONDecodeError, FileNotFoundError, KeyError):
            print("⚠️  数据文件损坏，已重置为空列表。")
            self.items = []

    def _save(self):
        """保存数据到JSON文件。"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in self.items], f, ensure_ascii=False, indent=2)

    def add(self, content, priority="中", due_date=None):
        """添加一个新的待办事项。"""
        if not content or not content.strip():
            print("❌ 内容不能为空！")
            return False
        item = TodoItem(content.strip(), priority, due_date)
        self.items.append(item)
        self._save()
        print(f"✅ 已添加: {item}")
        return True

    def list_all(self, sort_by="priority", status_filter="all"):
        """
        查看待办事项列表。

        :param sort_by: "priority" 按优先级降序, "due_date" 按截止日期升序
        :param status_filter: "all" 全部, "pending" 未完成, "done" 已完成
        """
        # 筛选
        if status_filter == "pending":
            filtered = [item for item in self.items if not item.completed]
        elif status_filter == "done":
            filtered = [item for item in self.items if item.completed]
        else:
            filtered = list(self.items)

        if not filtered:
            status_msg = {"all": "没有任何待办事项",
                         "pending": "没有未完成的待办事项",
                         "done": "没有已完成的待办事项"}
            print(f"📭 {status_msg.get(status_filter, '没有任何待办事项')}")
            return

        # 排序
        if sort_by == "due_date":
            def sort_key(item):
                if item.due_date:
                    return (0, item.due_date)
                return (1, "")
            filtered.sort(key=sort_key)
        else:  # priority
            filtered.sort(key=lambda x: x.priority, reverse=True)

        # 显示
        status_label = {"all": "全部", "pending": "未完成", "done": "已完成"}
        sort_label = {"priority": "优先级(高→低)", "due_date": "截止日期(近→远)"}

        print(f"\n{'='*60}")
        print(f"  待办事项列表 | 筛选: {status_label[status_filter]} | 排序: {sort_label[sort_by]}")
        print(f"{'='*60}")
        for i, item in enumerate(filtered, 1):
            print(f"{i:3d}. {item}")
        print(f"{'='*60}")
        print(f"  共 {len(filtered)} 项")
        print(f"{'='*60}\n")

    def mark_done(self, todo_id):
        """标记指定ID的待办事项为已完成。"""
        for item in self.items:
            if item.id == todo_id:
                if item.completed:
                    print(f"⚠️  该项已完成: {item.short_str()}")
                    return False
                item.completed = True
                self._save()
                print(f"✅ 已标记完成: {item.short_str()}")
                return True
        print(f"❌ 未找到ID为 {todo_id} 的待办事项")
        return False

    def delete_done(self):
        """删除所有已完成的待办事项。"""
        done_items = [item for item in self.items if item.completed]
        if not done_items:
            print("📭 没有已完成的待办事项可删除。")
            return False
        self.items = [item for item in self.items if not item.completed]
        self._save()
        print(f"🗑️  已删除 {len(done_items)} 条已完成事项:")
        for item in done_items:
            print(f"   - {item.short_str()}")
        return True

    def delete_by_id(self, todo_id):
        """删除指定ID的待办事项（无论是否完成）。"""
        for i, item in enumerate(self.items):
            if item.id == todo_id:
                removed = self.items.pop(i)
                self._save()
                print(f"🗑️  已删除: {removed.short_str()}")
                return True
        print(f"❌ 未找到ID为 {todo_id} 的待办事项")
        return False

    def stats(self):
        """显示统计信息。"""
        total = len(self.items)
        done = sum(1 for item in self.items if item.completed)
        pending = total - done

        if total == 0:
            print("📭 没有任何待办事项。")
            return

        print(f"\n{'='*40}")
        print(f"  待办事项统计")
        print(f"{'='*40}")
        print(f"  总计:     {total} 项")
        print(f"  已完成:   {done} 项")
        print(f"  未完成:   {pending} 项")
        if total > 0:
            print(f"  完成率:   {done/total*100:.1f}%")
        print(f"{'='*40}\n")
