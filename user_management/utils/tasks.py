from utils.logger import logger
import time


def send_welcome_email(email: str, name: str):
    time.sleep(2)
    logger.info(f"Welcome email sent to {email} for user {name}")


def log_user_action(user_id: int, action: str):
    logger.info(f"Audit log: user {user_id} performed {action}")
