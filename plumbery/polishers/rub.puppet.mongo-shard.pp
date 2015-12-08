class { '::ntp':
    servers => ['pool.ntp.org'],
  }
  
class {'::mongodb::globals':
  manage_package_repo => true,
}->
class {'::mongodb::server': 
  ensure   => true,
  bind_ip	=> '0.0.0.0',
  port    => 27018,
  verbose => true,
  shardsvr  => true,
  replset => 'rsmain',
#  replset_members => ['192.168.50.12:27018', '192.168.50.13:27018'],
}
