#!/bin/bash -eu

install_packages() {
  package_list="$@"

  sudo systemctl stop apt-daily.service
  sudo systemctl stop apt-daily.timer
  sudo systemctl kill --kill-who=all apt-daily.service
  sudo killall apt apt-get
  sleep 15;

  [ -e /var/lib/apt/lists/lock ]  && sudo rm /var/lib/apt/lists/lock
  [ -e  /var/cache/apt/archives/lock ] && sudo rm /var/cache/apt/archives/lock
  [ -e  /var/lib/dpkg/lock ] && sudo rm /var/lib/dpkg/lock
  [ -e /var/lib/dpkg/lock-frontend ] && sudo rm /var/lib/dpkg/lock*

  # wait until `apt-get updated` has been killed
  while ! (sudo systemctl list-units --all apt-daily.service | egrep -q "failed|dead"); do
      echo "waiting for daily.service to die :: current Status:"
      sudo systemctl list-units --all apt-daily.service|egrep "failed|dead"
      ps auwwx|grep apt|grep -v grep
      sleep 5;
  done

  echo -e "\n\nInstalling the following packages: ${package_list}"
  sudo apt-get update -qq
  sudo apt-get install -qq --no-install-recommends ${package_list}
  sudo rm -rf /var/lib/apt/lists/*
  sudo apt-get autoclean -qq
  sudo apt-get clean
}

install_deb_packages() {
  package_list="$@"

  sudo systemctl stop apt-daily.service
  sudo systemctl stop apt-daily.timer
  sudo systemctl kill --kill-who=all apt-daily.service
  sleep 15;

  # wait until `apt-get updated` has been killed
  while ! (sudo systemctl list-units --all apt-daily.service | egrep -q "failed|dead"); do
      echo "waiting for daily.service to die :: current Status:"
      sudo systemctl list-units --all apt-daily.service|egrep "failed|dead"
      ps auwwx|grep apt|grep -v grep
      sleep 5;
  done

  echo -e "\n\nInstalling the following packages: ${package_list}"
  sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' update
  sudo apt-get install -qq --no-install-recommends ${package_list}
  sudo rm -rf /var/lib/apt/lists/*
  sudo apt-get autoclean -qq
  sudo apt-get clean
}


remove_packages() {
  package_list="$@"
  echo -e "\n\nRemoving the following packages: ${package_list}"
  sudo apt-get update -qq
  sudo apt-get remove -q -y --purge ${package_list}
  rm -rf /var/lib/apt/lists/*
  sudo apt-get autoclean -qq
  sudo apt-get clean
}

add_user() {
  user=${1:-}
  name=${2:-}
  home=${3:-}
  uid=${4:-}
  gid=${5:-}
  groups=${6:-}

  [[ -n ${name} ]] && name="-c \"${name}\""
  [[ -n ${home} ]] && home="-d ${home}"
  [[ -n ${uid} ]] && uid="-u ${uid}"
  [[ -n ${gid} ]] && gid="-g ${gid}"
  [[ -n ${groups} ]] && groups="-G \"${groups}\""
  echo -e "running sudo useradd ${name} ${home} ${uid} ${gid} ${groups} -m ${user}\n"
  sudo useradd ${name} ${home} ${uid} ${gid} ${groups} -m ${user}
  #sudo useradd -c "Jenkins User" -d "${JENKINS_HOME}" -u 119 -g 119 -m jenkins
}

add_group() {
  group=${1:-}
  group_id=${2:-}
  [[ -n ${group_id} ]] && group_id="-g ${group_id}"

  sudo groupadd ${group_id} ${group}
}

make_dir() {
  path="${1:-}"
  owner="${2:-}"
  group="${3:-$owner}"
  permissions="${4:-}"
  set_sudo=""

  if [ ${owner} == "root" ] || [ ${group} == "root" ]; then
    set_sudo="sudo"
  fi

  [[ -n ${path} ]] && [[ -e ${path} ]] || mkdir -p ${path}
  [[ -n ${owner} ]] && ${set_sudo} chown ${owner}:${group} ${path}
  [[ -n ${permissions} ]] && ${set_sudo} chmod ${permissions} ${path}
}

copy_files() {
  src="${1:-}"
  dst="${2:-}"
  owner="${3:-}"
  group="${4:-$owner}"
  permissions="${5:-}"
  set_sudo=""
  src_end=${src: -1}
  dst_end=${dst: -1}
  shopt -s dotglob

  if [ ${owner} == "root" ] || [ ${group} == "root" ]; then
    set_sudo="sudo"
  fi

  if [ -d "${src}" ]; then
    echo -e "\nThe source is a directory making sure all files inside dir are copied\n"
    if [[ "${src_end}" != '/' ]] || [[ ${src_end} != '*' ]]; then
        src="${src}/*"
    fi
    if [[ "${dst_end}" != "/" ]]; then
        dst="${dst}/"
    fi
  elif [[ "${src_end}" == '/' ]] || [[ ${src_end} == '*' ]]; then
    echo -e "\nThe source is a directory making sure all files inside dir are copied\n"
    if [[ "${dst_end}" != "/" ]]; then
        dst="${dst}/"
    fi
  fi
  src_end=${src: -1}
  dst_end=${dst: -1}
  echo -e "Running the following Copy Command: cp -rpfv ${src} ${dst}\n"

  [[ -n ${src} ]] && [[ -n ${dst} ]] && cp -rpf ${src} ${dst}
  if [[ "${dst_end}" == "/" ]]; then
    dst="${dst}*"
  fi
  echo -e "Changing ownership as follows: chown ${owner}:${group} ${dst}"
  [[ -n ${owner} ]] && ${set_sudo} chown ${owner}:${group} ${dst}
  echo -e "Changing permissions as follows: chmod ${permissions} ${dst}"
  [[ -n ${permissions} ]] && ${set_sudo} chmod ${permissions} ${dst}
  shopt -u dotglob
}


