from requests.exceptions import ConnectionError
import requests
from time import time

valid = 0
offline = 0
invalid = 0

def time_request(url):
    """Sends a request to `url`, times how long it takes, and the time taken and resulting number."""
    global valid, offline, invalid

    start = time()
    result = ''
    try:
        response = requests.get(url)
        end = time()
    except ConnectionError:
        end = time()
        # Web service isn't up anymore for whatever reason
        result = 'ConnectionError'
        offline += 1
    
    if len(result) == 0:
        try:
            result = int(response.text)
            valid += 1
        except ValueError:
            # Somebody can't read instructions and returned HTML for some reason
            result = 'InvalidResponse'
            invalid += 1
    
    return (end - start, result)

# Public IP address of current device
ip = requests.get('http://myip.dnsomatic.com').text

with open('urls.txt') as targets:
    for target in targets:
        if target == '':
            continue

        (region, url) = tuple(target.split('@'))
        # Clean up the garbage input from idiots allergic to reading instructions
        region = region.strip().lower()
        if region.count('_') > 3:
            # Dunces can't tell the difference between a dash and an underscore
            region = region.replace('_', '-', 1)

        url = url.strip()
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://%s' % url
        
        (seconds, result) = time_request(url)

        # [from_ip_address]: [Region]_[zone]_[VM|app]_[Java|Python]@1.2.3.4 time random_number
        print('%s: %s@%s %ss %s' % (ip, region, url, seconds, result))

print('%s valid' % valid)
print('%s offline' % offline)
print('%s invalid' % invalid)
print('%d total' % (valid + offline + invalid))
