require 'spec_helper'

describe 'ssh daemon' do
  it 'has a running service of ssh' do
    expect(service('ssh')).to be_running
  end
  it 'responds on port 22' do
    expect(port 22).to be_listening 'tcp'
  end
end

describe 'kernel' do
  it 'has a kernel version at least > 4.8.x' do
    # this is required by Cilium
    major, minor, patch = `uname -r`.split('-')[0].split('.')
    expect(major.to_i).to be >= 4
    expect(minor.to_i).to be >= 8
  end
end

describe file('/proc/sys/net/ipv4/ip_forward') do
  its(:content) { should contain /1/ }
end

# %w{'sysdig', 'host', 'tcpdump', 'telnet', 'kubectl'}.each do |name|
#   describe package(name) do
#     it { should be_installed }
#   end
# end

# TODO: the following check should be in place, otherwise Cilium will not work:
# # cat config-4.4.0-1065-aws | grep BPF
# CONFIG_BPF=y
# CONFIG_BPF_SYSCALL=y
# CONFIG_BPF_JIT_ALWAYS_ON=y
# CONFIG_NETFILTER_XT_MATCH_BPF=m
# CONFIG_NET_CLS_BPF=m
# CONFIG_NET_ACT_BPF=m
# CONFIG_BPF_JIT=y
# CONFIG_HAVE_BPF_JIT=y
# CONFIG_HAVE_EBPF_JIT=y
# CONFIG_BPF_EVENTS=y
# CONFIG_TEST_BPF=m
