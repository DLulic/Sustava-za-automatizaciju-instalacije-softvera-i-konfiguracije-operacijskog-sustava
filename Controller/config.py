import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration management for the application."""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.config_file = Path("Storage") / "config.json"
        self.data_file = Path("Storage") / "data.json"
        self._config_cache: Optional[Dict[str, Any]] = None
        self._data_cache: Optional[Dict[str, Any]] = None
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration data with caching."""
        if self._config_cache is None:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
            else:
                self._config_cache = {}
        return self._config_cache
    
    def get_data(self) -> Dict[str, Any]:
        """Get data with caching."""
        if self._data_cache is None:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self._data_cache = json.load(f)
            else:
                self._data_cache = {}
        return self._data_cache
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration data."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self._config_cache = config
    
    def save_data(self, data: Dict[str, Any]) -> None:
        """Save data."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._data_cache = data
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update specific configuration values."""
        config = self.get_config()
        config.update(updates)
        self.save_config(config)
    
    def update_data(self, updates: Dict[str, Any]) -> None:
        """Update specific data values."""
        data = self.get_data()
        data.update(updates)
        self.save_data(data)
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """Get MySQL configuration."""
        config = self.get_config()
        required_fields = ["mysql_host", "mysql_port", "mysql_user", "mysql_password", "mysql_database"]
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing MySQL configuration fields: {missing_fields}")
        
        return {field: config[field] for field in required_fields}
    
    def get_windows_key(self) -> str:
        """Get Windows activation key."""
        return self.get_config().get('windows_key', '')
    
    def get_computer_name(self) -> str:
        """Get computer name."""
        return self.get_data().get('Naziv računala', '')
    
    def get_functions_path(self) -> Path:
        """Get path to Functions directory."""
        return Path("Functions")
    
    def clear_cache(self) -> None:
        """Clear configuration and data cache."""
        self._config_cache = None
        self._data_cache = None

# Global instance
config_manager = ConfigManager()
