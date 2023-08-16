#!/bin/bash
export BINANCE_API_KEY="02SDcYtuupovzMGoZzRyS8SjlKeLgUlUjjFOidH3uoQGHWRLt0i0uL2mGq3nLIlu"
export BINANCE_API_SECRET="Nm7AQJj3baXgPQSrOeZkIBjzJJ8IdwdlBGLTY5uv0FcOriIMFKyWux9gZAeUIa2B"
export INFLUX_HOST=$(hostname -I | awk '{print $1}')
export INFLUX_PORT="8086"
export INFLUXDB_TOKEN="6xXzmPMy7GSb3gSYw6KgLoPQVOD_AU1BXFlBPDw0cQMWSvD-qi6wLf9brYw3kipcrp3E30atYqeK8L7JK3GiVQ=="
export INFLUX_DATABASE="stockdata"
export INFLUX_ORG="stockdata"


# source /home/ubuntu/stock-venv/bin/activate
# python3 /home/ubuntu/stock-venv/bin/python reader.py
sudo docker run -it --rm \
    -e BINANCE_API_KEY=$BINANCE_API_KEY \
    -e BINANCE_API_SECRET=$BINANCE_API_SECRET \
    -e INFLUX_HOST=$INFLUX_HOST \
    -e INFLUX_PORT=$INFLUX_PORT \
    -e INFLUXDB_TOKEN=$INFLUXDB_TOKEN \
    -e INFLUX_DATABASE=$INFLUX_DATABASE \
    -e INFLUX_ORG=$INFLUX_ORG \
    -v /home/ubuntu/stock-venv:/venv -v $PWD:/app python /venv/bin/python /app/reader.py