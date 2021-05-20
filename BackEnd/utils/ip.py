def get_client_ip(x_forwarded_for, remote_addr):
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = remote_addr
    if ip and ':' in ip:  # IPV6
        ip = '127.0.0.1'  # Ping++ API only supports IPV4
    return ip


def get_ip_by_request(request):
    real_ip = request.META.get('HTTP_ALI_CDN_REAL_IP') or request.META.get(
        'HTTP_X_REAL_IP')
    if real_ip:
        return real_ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    remote_addr = request.META.get('REMOTE_ADDR')
    return get_client_ip(x_forwarded_for, remote_addr)
