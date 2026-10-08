package { 'haproxy':
  ensure => installed,
}

service { 'haproxy':
  ensure  => running,
  enable  => true,
}

file { '/etc/haproxy/haproxy.cfg':
  ensure => file,
  source => 'file:///tmp/haproxy.cfg',
  owner  => 'root',
  group  => 'root',
  mode   => '0644',
  notify => Service['haproxy'],
}
