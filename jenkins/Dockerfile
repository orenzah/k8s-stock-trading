FROM jenkins/jenkins as jenkins
RUN jenkins-plugin-cli --plugins kubernetes workflow-aggregator git configuration-as-code docker-plugin docker-workflow
USER root
ADD ./ci/requirements.txt /ci/requirements.txt
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https ca-certificates curl gnupg2 software-properties-common sudo \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && apt-key fingerprint 0EBFCD88 \
    && add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" \
    && apt-get update && \
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
    &&  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    &&  install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    &&  rm kubectl \
    && curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh \
    && rm get_helm.sh 
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3.11-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    python3 -m pip install --upgrade pip && python3 -m pip install -r /ci/requirements.txt && \
    rm -rf /root/.cache/pip && \
    rm -rf /ci/requirements.txt

RUN echo "jenkins ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
    && usermod -a -G docker jenkins
ADD ./jenkins/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["bash", "/entrypoint.sh"]

