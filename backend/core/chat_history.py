import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

class ChatHistory:
    def __init__(self, storage_dir: str = "chat_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.current_window: Optional[str] = None
        self.messages: Dict[str, List[Dict]] = {}
        self._load_existing_history()
    
    def _load_existing_history(self) -> None:
        """加载已存在的对话历史"""
        for file in self.storage_dir.glob("*.json"):
            try:
                window_id = file.stem
                with open(file, "r", encoding="utf-8") as f:
                    self.messages[window_id] = json.load(f)
            except Exception as e:
                print(f"加载对话历史失败 {file}: {str(e)}")
    
    def create_window(self) -> str:
        """创建新的对话窗口"""
        window_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.messages[window_id] = []
        self.current_window = window_id
        return window_id
    
    def add_message(self, role: str, content: str, window_id: Optional[str] = None) -> None:
        """添加新的对话消息"""
        target_window = window_id or self.current_window
        if not target_window:
            target_window = self.create_window()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if target_window not in self.messages:
            self.messages[target_window] = []
        
        self.messages[target_window].append(message)
        self._save_window(target_window)
    
    def get_messages(self, window_id: Optional[str] = None) -> List[Dict]:
        """获取指定窗口的所有消息"""
        target_window = window_id or self.current_window
        if not target_window or target_window not in self.messages:
            return []
        return self.messages[target_window]
    
    def _save_window(self, window_id: str) -> None:
        """保存指定窗口的对话历史"""
        if window_id not in self.messages:
            return
        
        file_path = self.storage_dir / f"{window_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.messages[window_id], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败 {window_id}: {str(e)}")
    
    def list_windows(self) -> List[str]:
        """列出所有对话窗口"""
        return list(self.messages.keys())
    
    def delete_window(self, window_id: str) -> bool:
        """删除指定的对话窗口"""
        if window_id not in self.messages:
            return False
        
        file_path = self.storage_dir / f"{window_id}.json"
        try:
            if file_path.exists():
                file_path.unlink()
            del self.messages[window_id]
            if self.current_window == window_id:
                self.current_window = None
            return True
        except Exception as e:
            print(f"删除对话历史失败 {window_id}: {str(e)}")
            return False