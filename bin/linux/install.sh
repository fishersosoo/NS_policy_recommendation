#!/usr/bin/env bash
SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
cd $SHELL_FOLDER
yum -y install epel-release
# install java
yum -y install lrzsz zlib* openssl-devel openssl
rpm -ivh jdk-8u191-linux-x64.rpm
JAVA_HOME=/usr/java/jdk1.8.0_191-amd64
CLASSPATH=.:$JAVA_HOME/lib/tools.jar
PATH=$JAVA_HOME/bin:$PATH
export JAVA_HOME CLASSPATH PATH

rm -rf /usr/bin/java
rm -rf /usr/bin/javac
ln -s /usr/java/jdk1.8.0_191-amd64/bin/java /usr/bin/java
ln -s /usr/java/jdk1.8.0_191-amd64/bin/javac /usr/bin/javac
/usr/java/jdk1.8.0_191-amd64/bin/unpack200 /usr/java/jdk1.8.0_191-amd64/jre/lib/rt.pack /usr/java/jdk1.8.0_191-amd64/jre/lib/rt.jar
/usr/java/jdk1.8.0_191-amd64/bin/unpack200 /usr/java/jdk1.8.0_191-amd64/jre/lib/jsse.pack /usr/java/jdk1.8.0_191-amd64/jre/lib/jsse.jar
/usr/java/jdk1.8.0_191-amd64/bin/unpack200 /usr/java/jdk1.8.0_191-amd64/jre/lib/charsets.pack /usr/java/jdk1.8.0_191-amd64/jre/lib/charsets.jar

# install python
yum -y groupinstall development zlib-devel
tar xJf Python-3.6.7.tar.xz
cd Python-3.6.7
./configure
make
make install
rm -rf /usr/bin/python3
rm -rf /usr/bin/pip3
ln -s /usr/local/python3/bin/python3 /usr/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
cd ..

# install neo4j
rpm --import https://debian.neo4j.org/neotechnology.gpg.key
cat << EOF >  /etc/yum.repos.d/neo4j.repo
[neo4j]
name=Neo4j RPM Repository
baseurl=https://yum.neo4j.org/stable
enabled=1
gpgcheck=1
EOF

NEO4J_ACCEPT_LICENSE_AGREEMENT=yes yum -y install neo4j-enterprise-3.5.0
cp neo4j.conf /etc/neo4j/neo4j.conf
neo4j start
neo4j stop
# restore data
neo4j-admin restore --from=db_backup/graph.db --database=graph.db
neo4j-admin set-initial-password 1995
neo4j-admin set-default-admin neo4j
neo4j start

yum -y install policycoreutils-python

# install mongodb
cat << EOF >  /etc/yum.repos.d/mongodb-enterprise.repo
[mongodb-enterprise]
name=MongoDB Enterprise Repository
baseurl=https://repo.mongodb.com/yum/redhat/7Server/mongodb-enterprise/4.0/x86_64/
gpgcheck=0
enabled=1
EOF
yum -y install mongodb-enterprise
semanage port -a -t mongod_port_t -p tcp 8001
cp mongod.conf /etc/mongod.conf
systemctl start mongod.service

# restore data
mongorestore db_backup/mongo_data --gzip
wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
rpm -ivh epel-release-6-8.noarch.rpm
yum -y install libreoffice libreoffice-headless unoconv redis gcc-c++

redis-server redis.conf
# setup python env
pip3 install virtualenv
cd NS_policy_recommendation
mkdir venv
virtualenv --no-site-packages venv
source venv/bin/activate
pip install -r requirements.txt

echo $SHELL_FOLDER/NS_policy_recommendation/ns_ai_system> venv/lib/python3.6/site-packages/ns_ai_system.pth
