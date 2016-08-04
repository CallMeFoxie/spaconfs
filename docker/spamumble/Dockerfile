FROM ubuntu:16.04
MAINTAINER Ashley

RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends --no-install-suggests
RUN apt-get install -y --no-install-recommends --no-install-suggests ice35-translators python-zeroc-ice wget ice35-slice ca-certificates
RUN apt-get install -y --no-install-recommends --no-install-suggests python python-mysqldb python-passlib python-pythonmagick python-bcrypt
COPY spamumble/ /opt/spamumble/
COPY compile.sh /opt/compile.sh
RUN /opt/compile.sh
RUN apt-get remove --purge -y ice35-translators wget ice35-slice wget ca-certificates
RUN apt-get autoremove -y
RUN apt-get clean

ENTRYPOINT ["/usr/bin/python", "-u", "/opt/spamumble/__init__.py"]
