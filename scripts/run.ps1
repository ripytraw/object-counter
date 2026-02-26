param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

function Download-Model {
    if (-not (Test-Path "tmp/model/$env:TF_MODEL_NAME/1")) {

        Write-Host "Downloading model: $env:TF_MODEL_NAME"

        New-Item -ItemType Directory -Force -Path "tmp/model" | Out-Null

        $url = "http://download.tensorflow.org/models/object_detection/${env:TF_MODEL_NAME}_coco_2018_03_29.tar.gz"
        Invoke-WebRequest -Uri $url -OutFile "tmp/model.tar.gz"

        tar -xzvf tmp/model.tar.gz -C tmp/model

        New-Item -ItemType Directory -Force -Path "tmp/model/$env:TF_MODEL_NAME/1" | Out-Null

        Move-Item `
            "tmp/model/${env:TF_MODEL_NAME}_coco_2018_03_29/saved_model/saved_model.pb" `
            "tmp/model/$env:TF_MODEL_NAME/1"

        Remove-Item "tmp/model.tar.gz"
        Remove-Item -Recurse -Force "tmp/model/${env:TF_MODEL_NAME}_coco_2018_03_29"

        Write-Host "Model ready."
    }
    else {
        Write-Host "Model already exists."
    }
}

switch ($Command) {

    "dev" {
        $env:MODEL_TYPE = "fake"
        $env:COUNT_BACKEND_TYPE = "inmemory"
        Write-Host "Running locally in DEV mode..."
        python -m counter.entrypoints.webapp
    }

    "prod-up" {

        if (-not $env:MODEL_TYPE) { $env:MODEL_TYPE = "tensorflow" }
        if (-not $env:COUNT_BACKEND_TYPE) { $env:COUNT_BACKEND_TYPE = "postgres" }
        if (-not $env:TF_MODEL_NAME) { $env:TF_MODEL_NAME = "ssd_mobilenet_v2" }

        if (-not $env:POSTGRES_USER) { $env:POSTGRES_USER = "test" }
        if (-not $env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD = "test" }
        if (-not $env:POSTGRES_DB) { $env:POSTGRES_DB = "test_db" }
        if (-not $env:MONGO_DB) { $env:MONGO_DB = "prod_counter" }
        if (-not $env:DATABASE_URL) {
            $env:DATABASE_URL = "postgresql+psycopg2://$($env:POSTGRES_USER):$($env:POSTGRES_PASSWORD)@postgres:5432/$($env:POSTGRES_DB)"
        }

        Download-Model
        docker compose up -d --build
    }

    "prod-down" {
        docker compose down
    }

    default {
        Write-Host "Usage:"
        Write-Host ".\scripts\run.ps1 dev"
        Write-Host ".\scripts\run.ps1 prod-up"
        Write-Host ".\scripts\run.ps1 prod-down"
        exit 1
    }
}
