class { '::ntp':
    servers => ['pool.ntp.org'],
  }

#install and configure Apache
class { 'apache':
	default_vhost => false,
    mpm_module => 'prefork',
}

include apache::mod::php

apache::vhost { 'vhost01.example.com':
  port    => '8080',
  docroot => '/var/www/vhost01',
}

# ensure info.php file exists
file { '/var/www/vhost01/index.php':
  ensure => file,
  content => '<?php  phpinfo(); ?>',    # phpinfo code
}
