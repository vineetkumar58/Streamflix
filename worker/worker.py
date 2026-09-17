import json
import os
import time
import pika

HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
USER = os.getenv("RABBITMQ_USER", "streamflix")
PASSWORD = os.getenv("RABBITMQ_PASSWORD", "streamflix_password")

QUEUE = "streamflix_jobs"


def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(USER, PASSWORD)

    parameters = pika.ConnectionParameters(
        host=HOST,
        port=PORT,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30
    )

    while True:
        try:
            print(f"Connecting to RabbitMQ at {HOST}:{PORT}...", flush=True)

            connection = pika.BlockingConnection(parameters)

            print("Connected to RabbitMQ.", flush=True)

            return connection

        except Exception as error:
            print(
                f"RabbitMQ connection failed: {error}",
                flush=True
            )
            print("Retrying in 5 seconds...", flush=True)
            time.sleep(5)


def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)

        print("Received job:", flush=True)
        print(message, flush=True)

        print("Processing job...", flush=True)

        # Background processing will go here later.

        print("Job completed.", flush=True)

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

    except Exception as error:
        print(f"Job processing failed: {error}", flush=True)

        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True
        )


def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE,
        durable=True
    )

    channel.basic_qos(
        prefetch_count=1
    )

    channel.basic_consume(
        queue=QUEUE,
        on_message_callback=process_message
    )

    print(
        f"Worker started. Waiting for jobs on '{QUEUE}'...",
        flush=True
    )

    channel.start_consuming()


if __name__ == "__main__":
    main()
