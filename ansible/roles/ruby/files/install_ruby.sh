#!/bin/bash
set -x
set -e

if [ $(command -v ruby | wc -l) -eq 1 ];
  then
    echo 'Ruby already installed'
    exit 0
fi

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

RUBY_MAIN_VERSION=$1
RUBY_MINOR_VERSION=$2
cd /root
wget "https://cache.ruby-lang.org/pub/ruby/${RUBY_MAIN_VERSION}/ruby-${RUBY_MINOR_VERSION}.tar.gz"
tar xzvf "ruby-${RUBY_MINOR_VERSION}.tar.gz"
cd "ruby-${RUBY_MINOR_VERSION}"
./configure --prefix=/usr/local
make
make install
cd ~
rm -rf "ruby-${RUBY_MINOR_VERSION}"
