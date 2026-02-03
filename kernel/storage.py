import json
import os
import datetime
from typing import Dict, Any, Optional

class StorageManager:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.state_file = os.path.join(storage_dir, "world_state.json")
        
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

    def save_state(self, state_data: Dict[str, Any]) -> None:
        """
        Saves the serialized state dictionary to a JSON file.
        """
        try:
            # Atomic write pattern: write to temp, then rename
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            # Rename to actual file (atomic on POSIX, usually fine on Windows if replaced)
            if os.path.exists(self.state_file):
                os.remove(self.state_file)
            os.rename(temp_file, self.state_file)
            
            print(f"[{datetime.datetime.now()}] State saved to {self.state_file}")
            
        except Exception as e:
            print(f"FAILED TO SAVE STATE: {e}")

    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Loads the state dictionary from JSON file if it exists.
        """
        if not os.path.exists(self.state_file):
            return None
            
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"[{datetime.datetime.now()}] State loaded from {self.state_file}")
            return data
        except Exception as e:
            print(f"FAILED TO LOAD STATE: {e}")
            return None
