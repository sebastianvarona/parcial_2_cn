"""Consul service registration via HTTP API (no extra deps needed)."""
import os
import requests
import signal
import socket
import atexit


def _host_ip():
    """Resolve local IP that Consul can reach."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception:
        return '127.0.0.1'


def register_service(app, service_name, port, health_path='/health',
                     consul_host=None, consul_port=None):
    """Register this service in Consul and deregister on shutdown."""
    consul_host = consul_host or os.environ.get('CONSUL_HOST', 'consul')
    consul_port = consul_port or int(os.environ.get('CONSUL_PORT', '8500'))
    consul_enabled = os.environ.get('CONSUL_ENABLED', 'false').lower() == 'true'

    if not consul_enabled:
        app.logger.info(f'Consul disabled — skipping registration for {service_name}')
        return

    service_id = f'{service_name}-{_host_ip()}-{port}'
    address = _host_ip()

    payload = {
        'ID': service_id,
        'Name': service_name,
        'Address': address,
        'Port': port,
        'Check': {
            'HTTP': f'http://{address}:{port}{health_path}',
            'Interval': '15s',
            'Timeout': '5s',
            'DeregisterCriticalServiceAfter': '30s',
        },
    }

    consul_url = f'http://{consul_host}:{consul_port}'
    max_retries = 10
    for attempt in range(max_retries):
        try:
            resp = requests.put(
                f'{consul_url}/v1/agent/service/register',
                json=payload,
                timeout=5,
            )
            if resp.ok:
                app.logger.info(
                    f'Registered {service_name} in Consul '
                    f'(ID={service_id}, addr={address}:{port})'
                )
                break
            app.logger.warning(
                f'Consul registration returned {resp.status_code} '
                f'(attempt {attempt + 1}/{max_retries})'
            )
        except requests.RequestException as e:
            app.logger.warning(
                f'Consul registration failed (attempt {attempt + 1}/{max_retries}): {e}'
            )
        import time
        time.sleep(3)

    # Deregister on exit
    def _deregister():
        try:
            requests.put(
                f'{consul_url}/v1/agent/service/deregister/{service_id}',
                timeout=5,
            )
            app.logger.info(f'Deregistered {service_name} from Consul')
        except Exception:
            pass

    atexit.register(_deregister)
