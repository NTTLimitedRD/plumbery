class { '::ntp':
    servers => ['pool.ntp.org'],
  }
  
 class {'::mongodb::globals':
  manage_package_repo => true,
}->
class {'::mongodb::server': 
  ensure   => true,
  bind_ip	=> '0.0.0.0',
  port    => 27019,
  verbose => true,
  configsvr => true,
}