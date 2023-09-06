#!/bin/bash
if (( $EUID == 0 )); then	
	alias sudo=""
fi

sudo apt-get install update
sudo apt-get install -y python3 python3-pip
KUBECTL_PATH=/usr/local/bin/kubectl
if [ -f $KUEBCTL_PATH ]; then
	echo "kubectl exists in $KUEBCTL_PATH"
else
	curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
	sudo install -o root -g root -m 0755 kubectl $KUEBCTL_PATH
	rm -f kubectl
fi
HELM_PATH=/usr/local/bin/helm
if [ -f $HELM_PATH ]; then	
	echo "helm exists in $HELM_PATH"
else
	curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
	chmod 700 get_helm.sh
	sudo ./get_helm.sh
	rm -f get_helm.sh
fi
python3 -m pip install virtualenv
if [ ! -d "venv" ]; then
    python3 -m virtualenv venv
fi
source venv/bin/activate
pip install -r ./stocks/requirements.txt
pip install -r ./ci/requirements.txt
pip install -r ./gdelt/requirements.txt
