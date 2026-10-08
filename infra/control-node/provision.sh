#!/bin/bash
set -e

echo "=== Actualizando paquetes ==="
apt-get update -y

echo "=== Instalando dependencias ==="
apt-get install -y curl gnupg lsb-release software-properties-common git \
  openssh-client python3 python3-pip

echo "=== Instalando Terraform ==="
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://apt.releases.hashicorp.com/gpg | \
  gpg --dearmor -o /etc/apt/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
  > /etc/apt/sources.list.d/hashicorp.list
apt-get update -y
apt-get install -y terraform

echo "=== Instalando Ansible ==="
apt-add-repository --yes --update ppa:ansible/ansible
apt-get install -y ansible

echo "=== Versiones instaladas ==="
terraform version
ansible --version | head -1

echo "=== Control-node listo ==="
