package { ['ca-certificates', 'curl', 'gnupg', 'lsb-release']:
  ensure => installed,
}

file { '/etc/apt/keyrings':
  ensure => directory,
  mode   => '0755',
}

exec { 'add docker gpg key':
  command => '/usr/bin/curl -fsSL https://download.docker.com/linux/ubuntu/gpg | /usr/bin/gpg --dearmor -o /etc/apt/keyrings/docker.gpg',
  creates => '/etc/apt/keyrings/docker.gpg',
  require => [Package['curl', 'gnupg'], File['/etc/apt/keyrings']],
}

exec { 'add docker apt repo':
  command => '/usr/bin/echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(/usr/bin/lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list',
  creates => '/etc/apt/sources.list.d/docker.list',
  require => Exec['add docker gpg key'],
}

exec { 'apt update after docker repo':
  command     => '/usr/bin/apt-get update',
  refreshonly => true,
  subscribe   => Exec['add docker apt repo'],
}

# --- 2. Instalar Docker Engine + Compose ---
package { ['docker-ce', 'docker-ce-cli', 'containerd.io', 'docker-buildx-plugin', 'docker-compose-plugin']:
  ensure  => installed,
  require => [Exec['apt update after docker repo'], Exec['add docker gpg key']],
}

# --- 3. Habilitar el servicio Docker al inicio ---
service { 'docker':
  ensure  => running,
  enable  => true,
  require => Package['docker-ce'],
}

# --- 4. Desplegar /opt/microapp con el docker-compose ---
file { '/opt/microapp':
  ensure => directory,
  mode   => '0755',
}

file { '/opt/microapp/docker-compose.yml':
  ensure => file,
  source => 'file:///tmp/docker-compose.prod.yml',
  mode   => '0644',
}

# --- 5. Levantar los contenedores ---
exec { 'docker compose up':
  command => '/usr/bin/docker compose up -d --pull always',
  cwd     => '/opt/microapp',
  path    => ['/usr/bin', '/usr/sbin', '/bin', '/sbin'],
  onlyif  => '/usr/bin/test -f /opt/microapp/docker-compose.yml',
  require => [Service['docker'], File['/opt/microapp/docker-compose.yml']],
}
