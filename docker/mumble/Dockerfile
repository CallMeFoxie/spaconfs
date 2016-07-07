FROM ubuntu:16.04
MAINTAINER Ashley

COPY add-apt-repository.sh /tmp/apt-add-repository.sh
RUN /tmp/apt-add-repository.sh ppa:mumble/release
RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends --no-install-suggests
RUN apt-get install -y --no-install-recommends --no-install-suggests mumble-server

EXPOSE 64738/tcp 64738/udp 6502/tcp

VOLUME ["/conf"]

ENTRYPOINT ["/usr/sbin/murmurd", "-fg", "-v"]
CMD ["-ini", "/conf/murmur.ini"]
