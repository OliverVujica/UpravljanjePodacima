from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.core.kafka_producer import KafkaNotificationProducer

def create_database_notification(db: Session, user_id: int, message: str, notification_type: str, related_id: int = None):
    notification = Notification(user_id=user_id, content=message, notification_type=notification_type, related_id=related_id)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def send_like_notification(db: Session, post_author_id: int, liker_username: str, post_id: int):
    kafka_producer = KafkaNotificationProducer()
    
    notification_message = f"{liker_username} liked your post"
    kafka_producer.send_notification(user_id=post_author_id, message=notification_message, notification_type='post_like', related_id=post_id)
    
    create_database_notification(db, user_id=post_author_id, message=notification_message, notification_type='post_like', related_id=post_id)