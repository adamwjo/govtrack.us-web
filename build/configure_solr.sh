#!/usr/bin/env bash

# NOTE: This script needs to run with superuser (sudo) permissions.

set -ex

GOVTRACK_ROOT=$(realpath $(dirname $0)/..)

# First stop the jetty service, as we won't be able to successfully stop the
# running process after we overwrite the configuration.
if service jetty8 status > /dev/null
then
  service jetty8 stop
fi

# Download and unzip the solr installation package
if [ ! -f solr-4.10.2.tgz ]
then
  curl -LO https://archive.apache.org/dist/lucene/solr/4.10.2/solr-4.10.2.tgz
fi

if [ ! -d solr-4.10.2 ]
then
  tar xvzf solr-4.10.2.tgz
fi

cd solr-4.10.2

# Create a new configuration from the example
cp -R example govtrack

# Initialize a collection for each of bill and person types
if [ ! -d govtrack/solr/bill ]
then
  mv govtrack/solr/collection1 govtrack/solr/bill
  echo "name=bill" > govtrack/solr/bill/core.properties
  ln -f -s $GOVTRACK_ROOT/bill/solr/schema.xml govtrack/solr/bill/conf/schema.xml
fi

if [ ! -d govtrack/solr/person ]
then
  cp -R govtrack/solr/bill govtrack/solr/person
  echo "name=person" > govtrack/solr/person/core.properties
  ln -f -s $GOVTRACK_ROOT/person/solr/schema.xml govtrack/solr/person/conf/schema.xml
fi

# Copy Solr over to /opt
cp -R govtrack/* /opt/solr

# Set up jetty to serve Solr
cp $GOVTRACK_ROOT/build/solrconfig/jetty /etc/default/jetty8
cp $GOVTRACK_ROOT/build/solrconfig/jetty.conf /etc/jetty8/jetty.conf
cp $GOVTRACK_ROOT/build/solrconfig/jetty-logging.xml /opt/solr/etc/jetty-logging.xml

if ! id -u solr > /dev/null 2>&1
then
  useradd -d /opt/solr -s /sbin/false solr
fi

mkdir -p /var/log/solr
chown solr:solr -R /opt/solr
chown solr:solr -R /var/log/solr

service jetty8 start
