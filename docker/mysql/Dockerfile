FROM ubuntu:16.04
MAINTAINER Ashley

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get dist-upgrade -y --no-install-recommends --no-install-suggests
RUN apt-get install -y --no-install-recommends --no-install-suggests mysql-server
RUN mkdir /var/run/mysqld && chmod 0777 /var/run/mysqld && sed -i "/log_error/d" /etc/mysql/mysql.conf.d/mysqld.cnf
COPY initfile.txt /tmp/initfile.txt
RUN /usr/sbin/mysqld --init-file=/tmp/initfile.txt


EXPOSE 3306/tcp

VOLUME ["/data"]

ENTRYPOINT ["/usr/sbin/mysqld"]
CMD ["--defaults-extra-file=/data/my.cnf", "--console"]
