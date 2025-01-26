
# See:
# @/docs/dev_notes/docker_notes.md

FROM fedora:41

# Install dependencies:
RUN dnf -y install git
RUN dnf -y install which
RUN dnf -y install python
RUN dnf -y install jq
RUN dnf -y install nmap-ncat

# Setup an app user so the container doe not run as the root user:
RUN useradd argrelay
USER argrelay

WORKDIR /usr/local/argrelay.git

RUN git clone https://github.com/argrelay/argrelay.git .
# TODO: Automatically use the latest tag:
RUN git checkout -b argrelay v0.8.0.final

EXPOSE 8787

# Update to bind to 0.0.0.0 instad of 127.0.0.1:
# https://stackoverflow.com/a/54942153/441652
RUN sed -i "s/^\\([[:space:]]*server_host_name:[[:space:]]*\\)localhost/\\10.0.0.0/g" ./src/argrelay_app_bootstrap/sample_conf/argrelay_server.yaml

RUN ./exe/relay_demo.bash

CMD [ "./exe/relay_demo.bash" ]

