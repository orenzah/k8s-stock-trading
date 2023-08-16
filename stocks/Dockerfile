FROM python as base
ADD ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm -rf /app/requirements.txt

FROM base as app
ADD ./code /app
