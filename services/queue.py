import os
import json
import pika

def get_connection():
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = int(os.getenv("RABBITMQ_PORT", "5672"))
    user = os.getenv("RABBITMQ_USER", "streamflix")
    password = os.getenv("RABBITMQ_PASSWORD", "streamflix_password")

    credentials = pika.PlainCredentials(user, password)

    parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials
    )

    return pika.BlockingConnection(parameters)


def publish_message(queue_name, message):
    connection = get_connection()
    channel = connection.channel()

    channel.queue_declare(
        queue=queue_name,
        durable=True
    )

    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    connection.close()
