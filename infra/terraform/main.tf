locals {
  ssh_public_key = chomp(file(var.public_key_path))
  disk_bytes     = var.vm_disk_gb * 1024 * 1024 * 1024
}

# --
# Storage pool (directorio)
# --
resource "libvirt_pool" "micro_pool" {
  name = "micro_pool"
  type = "dir"
  path = "/var/lib/libvirt/images/micro_pool"
}

# --
# Red aislada (NAT) para los nodos target
# --
resource "libvirt_network" "micro_net" {
  name      = "micro_net"
  mode      = "nat"
  domain    = "micro.local"
  addresses = [var.network_cidr]
  autostart = true

  dhcp {
    enabled = true
  }
}

# --
# Volumen base (imagen cloud de Ubuntu 22.04)
# --
resource "libvirt_volume" "base" {
  name   = "ubuntu-2204-base.img"
  pool   = libvirt_pool.micro_pool.name
  source = var.base_image_path
  format = "qcow2"
}

# --
# Discos de las VMs (overlays sobre el volumen base)
# --
resource "libvirt_volume" "haproxy_disk" {
  name           = "vm-haproxy.qcow2"
  pool           = libvirt_pool.micro_pool.name
  base_volume_id = libvirt_volume.base.id
  size           = local.disk_bytes
}

resource "libvirt_volume" "microservices_disk" {
  name           = "vm-microservices.qcow2"
  pool           = libvirt_pool.micro_pool.name
  base_volume_id = libvirt_volume.base.id
  size           = local.disk_bytes
}

# --
# cloud-init: vm-haproxy
# --
resource "libvirt_cloudinit_disk" "haproxy_cloudinit" {
  name = "vm-haproxy-cloudinit.iso"
  pool = libvirt_pool.micro_pool.name

  user_data = <<-EOT
  #cloud-config
  hostname: vm-haproxy
  fqdn: vm-haproxy.micro.local
  manage_etc_hosts: true
  users:
    - name: ubuntu
      ssh_authorized_keys:
        - ${local.ssh_public_key}
      sudo: ['ALL=(ALL) NOPASSWD:ALL']
      shell: /bin/bash
  ssh_pwauth: false
  package_update: true
  runcmd:
    - wget -q https://apt.puppet.com/puppet8-release-jammy.deb -O /tmp/puppet8.deb
    - dpkg -i /tmp/puppet8.deb
    - apt-get update -y
    - apt-get install -y puppet-agent
    - ln -sf /opt/puppetlabs/bin/puppet /usr/local/bin/puppet
  EOT

  network_config = <<-EOT
  version: 2
  ethernets:
    ens3:
      match:
        macaddress: "52:54:00:11:22:33"
      dhcp4: false
      addresses:
        - ${var.haproxy_ip}/24
      routes:
        - to: default
          via: ${var.gateway_ip}
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
  EOT
}

# --
# cloud-init: vm-microservices
# --
resource "libvirt_cloudinit_disk" "microservices_cloudinit" {
  name = "vm-microservices-cloudinit.iso"
  pool = libvirt_pool.micro_pool.name

  user_data = <<-EOT
  #cloud-config
  hostname: vm-microservices
  fqdn: vm-microservices.micro.local
  manage_etc_hosts: true
  users:
    - name: ubuntu
      ssh_authorized_keys:
        - ${local.ssh_public_key}
      sudo: ['ALL=(ALL) NOPASSWD:ALL']
      shell: /bin/bash
  ssh_pwauth: false
  package_update: true
  runcmd:
    - wget -q https://apt.puppet.com/puppet8-release-jammy.deb -O /tmp/puppet8.deb
    - dpkg -i /tmp/puppet8.deb
    - apt-get update -y
    - apt-get install -y puppet-agent
    - ln -sf /opt/puppetlabs/bin/puppet /usr/local/bin/puppet
  EOT

  network_config = <<-EOT
  version: 2
  ethernets:
    ens3:
      match:
        macaddress: "52:54:00:11:22:44"
      dhcp4: false
      addresses:
        - ${var.microservices_ip}/24
      routes:
        - to: default
          via: ${var.gateway_ip}
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
  EOT
}

# --
# Dominios (VMs)
# --
resource "libvirt_domain" "vm_haproxy" {
  name      = "vm-haproxy"
  memory    = var.vm_memory
  vcpu      = var.vm_vcpu
  autostart = true

  cpu {
    mode = "host-passthrough"
  }

  cloudinit = libvirt_cloudinit_disk.haproxy_cloudinit.id

  network_interface {
    network_name = libvirt_network.micro_net.name
    mac          = "52:54:00:11:22:33"
  }

  disk {
    volume_id = libvirt_volume.haproxy_disk.id
  }

  graphics {
    type        = "vnc"
    listen_type = "none"
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  #
  # Approvisionamiento con Puppet
  #
  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = var.haproxy_ip
    private_key = file("${path.module}/${var.private_key_path}")
    timeout     = "5m"
  }

  provisioner "file" {
    source      = "${path.module}/../puppet/manifests/haproxy.pp"
    destination = "/tmp/puppet-manifest.pp"
  }

  provisioner "file" {
    source      = "${path.module}/../../haproxy/haproxy.cfg"
    destination = "/tmp/haproxy.cfg"
  }

  provisioner "remote-exec" {
    inline = [
      "for i in $(seq 1 60); do [ -x /opt/puppetlabs/bin/puppet ] && break; sleep 5; done",
      "sudo /opt/puppetlabs/bin/puppet apply /tmp/puppet-manifest.pp"
    ]
  }
}

resource "libvirt_domain" "vm_microservices" {
  name      = "vm-microservices"
  memory    = var.vm_memory
  vcpu      = var.vm_vcpu
  autostart = true

  cpu {
    mode = "host-passthrough"
  }

  cloudinit = libvirt_cloudinit_disk.microservices_cloudinit.id

  network_interface {
    network_name = libvirt_network.micro_net.name
    mac          = "52:54:00:11:22:44"
  }

  disk {
    volume_id = libvirt_volume.microservices_disk.id
  }

  graphics {
    type        = "vnc"
    listen_type = "none"
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  #
  # Approvisionamiento con Puppet (Opcional A)
  #
  connection {
    type        = "ssh"
    user        = "ubuntu"
    host        = var.microservices_ip
    private_key = file("${path.module}/${var.private_key_path}")
    timeout     = "5m"
  }

  provisioner "file" {
    source      = "${path.module}/../puppet/manifests/microservices.pp"
    destination = "/tmp/puppet-manifest.pp"
  }

  provisioner "file" {
    source      = "${path.module}/../../docker-compose.prod.yml"
    destination = "/tmp/docker-compose.prod.yml"
  }

  provisioner "remote-exec" {
    inline = [
      "for i in $(seq 1 60); do [ -x /opt/puppetlabs/bin/puppet ] && break; sleep 5; done",
      "sudo /opt/puppetlabs/bin/puppet apply /tmp/puppet-manifest.pp"
    ]
  }
}
