output "haproxy_ip" {
  description = "IP de vm-haproxy"
  value       = var.haproxy_ip
}

output "microservices_ip" {
  description = "IP de vm-microservices"
  value       = var.microservices_ip
}

output "domain_names" {
  description = "Nombres de los dominios libvirt creados"
  value = {
    haproxy       = libvirt_domain.vm_haproxy.name
    microservices = libvirt_domain.vm_microservices.name
  }
}
