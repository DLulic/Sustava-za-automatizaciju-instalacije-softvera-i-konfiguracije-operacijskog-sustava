import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from ttkbootstrap.dialogs import Messagebox
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from Controller.mysql import open_mysql_connection
from utils.logger import logger


class MysqlConfigFrame(ttk.Frame):
    def __init__(self, parent, config_path: str, config: Dict[str, Any], on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.config = config
        self.on_save = on_save
        self.entries: Dict[str, ttk.Entry] = {}
        fields = [
            ("mysql_host", "Host"),
            ("mysql_user", "Korisnik"),
            ("mysql_port", "Port"),
            ("mysql_password", "Lozinka"),
            ("mysql_database", "Baza")
        ]
        for i, (key, label) in enumerate(fields):
            ttk.Label(self, text=f"{label}:").grid(row=i, column=0, sticky="e", padx=10, pady=5)
            ent = ttk.Entry(self, width=25, show="*" if key == "mysql_password" else None)
            ent.grid(row=i, column=1, padx=10, pady=5)
            if config.get(key):
                ent.insert(0, str(config[key]))
            self.entries[key] = ent

        btn = ttk.Button(self, text="Spremi", command=self.save_and_continue, bootstyle=SUCCESS)
        btn.grid(row=len(fields), column=0, columnspan=2, pady=15)

    def save_and_continue(self) -> None:
        """Save configuration and test MySQL connection."""
        try:
            # Update config with form values
            for key, ent in self.entries.items():
                val = ent.get().strip()
                if key == "mysql_port":
                    try:
                        val = int(val)
                    except ValueError:
                        logger.warning(f"Invalid port number '{val}', using default 3306 in utils.logger", file=Path(__file__).name)
                        val = 3306
                self.config[key] = val
            
            # Save configuration to file
            try:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                logger.info(f"Configuration saved to {self.config_path}", file=Path(__file__).name)
            except Exception as e:
                logger.error(f"Failed to save configuration: {e}", file=Path(__file__).name)
                Messagebox.show_error("Save Error", f"Failed to save configuration:\n{e}")
                return

            # Test MySQL connection
            logger.info("Testing MySQL connection...", file=Path(__file__).name)
            try:
                time.sleep(0.5)  # Brief delay for UI responsiveness
                open_mysql_connection()
                logger.info("MySQL connection successful", file=Path(__file__).name)
                
                if self.on_save:
                    self.on_save()
                else:
                    logger.info("No callback provided, configuration saved successfully", file=Path(__file__).name)
                    
            except Exception as e:
                error_msg = f"Could not connect to MySQL:\n{e}"
                logger.error(f"MySQL connection failed: {e}", file=Path(__file__).name)
                Messagebox.show_error("MySQL Connection Error", error_msg)
                return  # Do not proceed, let user correct info
                
        except Exception as e:
            error_msg = f"Unexpected error during save: {e}"
            logger.error(error_msg, file=Path(__file__).name)
            Messagebox.show_error("Error", error_msg)
