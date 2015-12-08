class { '::ntp':
    servers => ['pool.ntp.org'],
  }

class {'::mongodb::globals':
  manage_package_repo => true,
}->
class {'::mongodb::server': 
  ensure   => true,
  port    => 27019,
  verbose => true,
  configsvr => true,
}
class {'::mongodb::mongos' :
  port => 27017,
  ensure   => true,
  configdb => ['192.168.50.8:27019','192.168.50.9:27019','192.168.50.10:27019'],
}
class {'::mongodb::client':}
