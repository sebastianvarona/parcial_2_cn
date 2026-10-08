variable "base_image_path" {
  description = "Ruta a la imagen cloud de Ubuntu 22.04 (qcow2)"
  type        = string
  default     = "/home/svarona/.local/share/libvirt/images/ubuntu-22.04-server-cloudimg-amd64.img"
}

variable "public_key_path" {
  description = "Llave pública SSH inyectada en las VMs (relativa al directorio terraform/)"
  type        = string
  default     = "../ssh/micro_id_rsa.pub"
}

variable "private_key_path" {
  description = "Llave privada SSH usada por los provisioners (relativa al directorio terraform/)"
  type        = string
  default     = "../ssh/micro_id_rsa"
}

variable "network_cidr" {
  description = "CIDR de la red aislada de los nodos target"
  type        = string
  default     = "192.168.100.0/24"
}

variable "gateway_ip" {
  description = "IP del gateway (host) en la red aislada"
  type        = string
  default     = "192.168.100.1"
}

variable "haproxy_ip" {
  description = "IP estática de vm-haproxy"
  type        = string
  default     = "192.168.100.3"
}

variable "microservices_ip" {
  description = "IP estática de vm-microservices"
  type        = string
  default     = "192.168.100.4"
}

variable "vm_memory" {
  description = "RAM (MB) por VM"
  type        = number
  default     = 2048
}

variable "vm_vcpu" {
  description = "vCPUs por VM"
  type        = number
  default     = 2
}

variable "vm_disk_gb" {
  description = "Tamaño de disco (GB) por VM"
  type        = number
  default     = 20
}
