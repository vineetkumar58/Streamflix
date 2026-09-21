import json
import os
import time
import pika
import mysql.connector

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "streamflix")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "streamflix_password")

DB_HOST = os.getenv("DB_HOST", "mysql")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "streamflix")
DB_PASSWORD = os.getenv("DB_PASSWORD", "streamflix_password")
DB_NAME = os.getenv("DB_NAME", "streamflix")

QUEUE = "streamflix_jobs"


def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(
        RABBITMQ_USER,
        RABBITMQ_PASSWORD
    )

    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30
    )

    while True:
        try:
            print(
                f"Connecting to RabbitMQ at "
                f"{RABBITMQ_HOST}:{RABBITMQ_PORT}...",
                flush=True
            )

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


def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def process_movie_job(message):
    movie_id = message.get("movie_id")

    if not movie_id:
        raise ValueError("movie_id is required")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, title, genre, release_year "
        "FROM movies WHERE id = %s",
        (movie_id,)
    )

    movie = cursor.fetchone()

    if not movie:
        cursor.close()
        connection.close()
        raise ValueError(f"Movie {movie_id} not found")

    print(
        f"Processing movie: {movie['title']} "
        f"(ID: {movie['id']})",
        flush=True
    )

    cursor.execute(
        """
        INSERT INTO job_logs
        (job_type, movie_id, status, message)
        VALUES (%s, %s, %s, %s)
        """,
        (
            message.get("type", "movie_processing"),
            movie_id,
            "completed",
            f"Processed movie: {movie['title']}"
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    print(
        f"Movie {movie_id} processed successfully.",
        flush=True
    )


def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)

        print(
            f"Received job: {message}",
            flush=True
        )

        process_movie_job(message)

        ch.basic_ack(
            delivery_tag=method.delivery_tag
        )

        print("Job acknowledged.", flush=True)

    except Exception as error:
        print(
            f"Job processing failed: {error}",
            flush=True
        )

        ch.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
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
