import time
import uuid
import re
from typing import Optional
from app.config import ALLOWED_USER_IDS

BLOCKED_PATTERNS = [
    "rm -rf /", "rm -rf /*", "format", "mkfs", "dd if=",
    "shutdown", "reboot", "poweroff", "halt", r"del /s /q C:\/",
    "reg delete", "net user", "passwd", "sudo su", "sudo -i",
    "chmod -R 777 /", "chown -R", "cipher /w", "bcdedit", "diskpart"
]

CONFIRM_PATTERNS = [
    "pip install", "npm install", "npm update", "git pull",
    "git reset", "git checkout", "systemctl restart", "service restart",
    "kill", "taskkill", "copy", "xcopy", "robocopy", "move", "mv",
    "rm", "del", "chmod", "chown"
]

# In-memory confirmation store: { confirm_id: {"user_id": int, "command": str, "expires_at": float} }
pending_confirmations = {}

def is_authorized(user_id: int, chat_type: str) -> bool:
    if chat_type != "private":
        return False
    if user_id not in ALLOWED_USER_IDS:
        return False
    return True

def _matches_pattern(pattern: str, command: str) -> bool:
    # Escape the pattern, but replace escaped spaces with \s+ to handle multiple spaces
    escaped = re.escape(pattern).replace(r'\ ', r'\s+')
    # Add word boundaries if it starts/ends with alphanumeric characters
    prefix = r'\b' if pattern[0].isalnum() else ''
    suffix = r'\b' if pattern[-1].isalnum() else ''
    return bool(re.search(prefix + escaped + suffix, command))

def categorize_command(command: str) -> str:
    # Check blocked first
    for pattern in BLOCKED_PATTERNS:
        if _matches_pattern(pattern, command):
            return "BLOCKED"
        
    # Check confirm
    for pattern in CONFIRM_PATTERNS:
        if _matches_pattern(pattern, command):
            return "CONFIRM"
        
    return "ALLOWED"

def create_confirmation(user_id: int, command: str) -> str:
    confirm_id = str(uuid.uuid4())[:8]
    pending_confirmations[confirm_id] = {
        "user_id": user_id,
        "command": command,
        "expires_at": time.time() + 60.0
    }
    return confirm_id

def get_and_clear_confirmation(confirm_id: str, user_id: int) -> Optional[str]:
    if confirm_id not in pending_confirmations:
        return None
    
    conf = pending_confirmations[confirm_id]
    del pending_confirmations[confirm_id]

    if conf["user_id"] != user_id:
        return None
    
    if time.time() > conf["expires_at"]:
        return None
    
    return conf["command"]