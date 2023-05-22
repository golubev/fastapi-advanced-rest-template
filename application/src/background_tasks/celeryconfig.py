from src.config import application_config

broker_url = application_config.get_rabbitmq_uri()

timezone = "UTC"

beat_schedule_filename = "./src/background_tasks/.celerybeat-schedule"

worker_redirect_stdouts = True
worker_redirect_stdouts_level = "WARNING"

task_default_queue = "default-queue"
task_default_exchange = "default-exchange"
task_default_exchange_type = "topic"
task_default_routing_key = "task.default"
