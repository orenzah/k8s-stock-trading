#!/bin/bash
set -e -x -o pipefail
sudo /etc/init.d/docker start
/usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"