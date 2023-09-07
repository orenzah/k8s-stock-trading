FROM jenkins/jenkins as jenkins
RUN jenkins-plugin-cli --plugins kubernetes workflow-aggregator git configuration-as-code docker-plugin docker-workflow
USER root
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
    rm -rf /var/lib/apt/lists/*
RUN echo "jenkins ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers



