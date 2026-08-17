#!/bin/bash

until cd /opt/deploy/intel_owl
do
    echo "Waiting for server volume..."
done

if [ "$AWS_SQS" = "True" ]
then
  queues="chatbot.fifo,config.fifo"
else
  queues="chatbot,broadcast,config"
fi

# Concurrency is intentionally low (-c 2): a chat turn is a long, LLM-bound ReAct run
# (soft_time_limit=300) that ends up serialized on the single Ollama backend, so a large pool
# would only spawn idle workers all blocked on the model. --time-limit=600 is a hard backstop
# comfortably above the task's 300s soft limit; it deliberately overrides the global
# task_time_limit=1800 (intel_owl/celery.py) for this LLM worker so a hung turn is reclaimed
# sooner.
ARGUMENTS="-A intel_owl.celery worker -n worker_chatbot --uid www-data --gid www-data --time-limit=600 --pidfile= -c 2 -Ofair -Q ${queues} -E --without-gossip"
if [[ $DEBUG == "True" ]] && [[ $DJANGO_TEST_SERVER == "True" ]];
then
    echo "Running celery with autoreload"
    python3 manage.py celery_reload -c "$ARGUMENTS"
else
  # shellcheck disable=SC2086
  /usr/local/bin/celery $ARGUMENTS
fi
