from confluent_kafka import Producer
import json
from app.config import settings

class KafkaNotificationProducer:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.producer = Producer({
                'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS
            })
        return cls._instance

    def send_notification(self, user_id, message, notification_type, related_id=None):
        notification_data = {
            'user_id': user_id,
            'message': message,
            'type': notification_type,
            'related_id': related_id
        }
        
        try:
            self.producer.produce(
                settings.KAFKA_NOTIFICATION_TOPIC, 
                key=str(user_id),
                value=json.dumps(notification_data).encode('utf-8')
            )
            self.producer.flush()
        except Exception as e:
            print(f"Kafka notification error: {e}")