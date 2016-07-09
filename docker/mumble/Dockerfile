FROM ubuntu:16.04
MAINTAINER Ashley

RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends --no-install-suggests
COPY add-apt-repository.sh /tmp/apt-add-repository.sh
RUN /tmp/apt-add-repository.sh ppa:mumble/release
RUN apt-get install -y --allow-unauthenticated --no-install-recommends --no-install-suggests mumble-server
RUN rm /etc/init.d/mumble-server

EXPOSE 64738/tcp 64738/udp 6502/tcp

VOLUME ["/data"]

ENTRYPOINT ["/usr/sbin/murmurd", "-fg", "-v"]
CMD ["-ini", "/data/murmur.ini"]
