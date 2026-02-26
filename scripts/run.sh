#!/usr/bin/env bash

set -e

COMMAND=$1

download_model() {
  if [ ! -d "tmp/model/${TF_MODEL_NAME}/1" ]; then
    echo "Downloading model: ${TF_MODEL_NAME}"

    mkdir -p tmp/model

    curl -L -o tmp/model.tar.gz \
      http://download.tensorflow.org/models/object_detection/${TF_MODEL_NAME}_coco_2018_03_29.tar.gz

    tar -xzvf tmp/model.tar.gz -C tmp/model

    mkdir -p tmp/model/${TF_MODEL_NAME}/1

    mv tmp/model/${TF_MODEL_NAME}_coco_2018_03_29/saved_model/saved_model.pb \
       tmp/model/${TF_MODEL_NAME}/1/

    chmod -R 755 tmp/model
    rm tmp/model.tar.gz
    rm -rf tmp/model/${TF_MODEL_NAME}_coco_2018_03_29

    echo "Model ready."
  else
    echo "Model already exists."
  fi
}

case "$COMMAND" in

  dev)
    export MODEL_TYPE=fake
    export COUNT_BACKEND_TYPE=inmemory
    echo "Running locally in DEV mode..."
    python -m counter.entrypoints.webapp
    ;;

  prod-up)
    export MODEL_TYPE=${MODEL_TYPE:-tensorflow}
    export COUNT_BACKEND_TYPE=${COUNT_BACKEND_TYPE:-postgres}
    export TF_MODEL_NAME=${TF_MODEL_NAME:-ssd_mobilenet_v2}

    export POSTGRES_USER=${POSTGRES_USER:-test}
    export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-test}
    export POSTGRES_DB=${POSTGRES_DB:-test_db}

    export MONGO_DB=${MONGO_DB:-prod_counter}
    
    export DATABASE_URL=${DATABASE_URL:-postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}}

    download_model
    docker compose up -d --build
    ;;

  prod-down)
    docker compose down
    ;;

  *)
    echo "Usage:"
    echo "./scripts/run.sh dev"
    echo "./scripts/run.sh prod-up"
    echo "./scripts/run.sh prod-down"
    exit 1
    ;;

esac