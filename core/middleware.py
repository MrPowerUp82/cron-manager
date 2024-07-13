import time, logging, os
from django.http import HttpResponseForbidden

def get_csf_allow_ip():
    command = 'cat /etc/csf/csf.allow'
    output = os.popen(command).read()
    # ips = [ip[:ip.rfind('#')].strip() if ip.rfind('#') > 0 else ip.strip() for ip in output.strip().split('\n') if ip and not ip.startswith('#')]
    return output

class IPBlockerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Captura o IP do cliente
        ip = self.get_client_ip(request)
        print(ip)
        
        # Verifica se o IP está na lista de bloqueados
        if not ip in get_csf_allow_ip():
            return HttpResponseForbidden(f"Forbidden: Your IP is blocked. {ip}")
        
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        # Captura o IP do cliente considerando proxies
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip