FROM ubuntu:16.04
MAINTAINER Ashley

RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends --no-install-suggests
RUN apt-get install -y --no-install-recommends --no-install-suggests oidentd
RUN apt-get autoremove -y
RUN apt-get clean
COPY oidentd.conf /etc/oidentd.conf

EXPOSE 113/tcp

ENTRYPOINT ["/usr/sbin/oidentd", "-i", "-p", "113", "-S"]
