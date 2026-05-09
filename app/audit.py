import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("TerminalRemote")

def log_event(event_type: str, user_id: int, details: str):
    logger.info(f"Event: {event_type} | User: {user_id} | Details: {details}")

def log_security_alert(user_id: int, reason: str):
    logger.warning(f"SECURITY ALERT | User: {user_id} | Reason: {reason}")