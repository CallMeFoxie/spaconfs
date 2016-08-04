FROM ubuntu:16.04
MAINTAINER Ashley

RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends --no-install-suggests
RUN apt-get install -y --no-install-recommends --no-install-suggests znc
RUN apt-get autoremove -y
RUN apt-get clean

EXPOSE 6668/tcp 6667/tcp

VOLUME ["/data"]

ENTRYPOINT ["/usr/bin/znc", "-f", "-r"]
CMD ["-d", "/data"]
