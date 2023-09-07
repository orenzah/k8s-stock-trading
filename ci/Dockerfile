FROM cr.zahtlv.freeddns.org/python-base as ci
ADD ./ci/requirements.txt /ci/requirements.txt
ADD ./main.* /ci/
RUN pip install --upgrade pip && pip install -r /ci/requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm -rf /ci/requirements.txt