import json
import time
import requests
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pytz
import threading  # Added for lock mechanism
from config.logging_config import logger
import re 

domain_statuses = {}

# Initialize a threading lock to prevent concurrent monitoring runs
monitor_lock = threading.Lock()

# List of domains to monitor
domains = [
    "901businessmail.com",
    "allenstristate.com",
    "allstatestruck.com",
    "amarillocustomhomes.com",
    "amarillodogboarding.com",
    "amarilloea.com",
    "amarillofp.com",
    "amarillopanhellenic.org",
    "amarillorealtors.org",
    "amarilloseniorcitizens.com",
    "amarillosparkviewrealty.com",
    "amarillothunder.com",
    "andrewsama.com",
    "apsama.com",
    "austinbikefarm.com",
    "badgerofwesttexas.com",
    "barfieldlawfirm.net",
    "bf-law.com",
    "bivinsfoundation.org",
    "bluemondayrealestate.com",
    "brownconsultingengineers.com",
    "budgriffin.com",
    "canyonrimconsulting.com",
    "cctxp.org",
    "charleysautos.com",
    "childrenslc.org",
    "christianchurchofgod.org",
    "cib-inc.com",
    "circlelirrigationtx.com",
    "collingsworthcountymuseum.org",
    "connerindustriestx.com",
    "crossroadscountrychurch.org",
    "deafsmithcountymuseum.org",
    "diamondwcorrals.com",
    "djamarillo.com",
    "dlockeinc.net",
    "dougricketts.com",
    "dovecreekequinerescue.org",
    "dukeelec.com",
    "dyersbbq.com",
    "ericspellmann.com",
    "evensontrucking.com",
    "familyphotoamarillo.com",
    "fimcrealty.com",
    "gatewaysupplytx.com",
    "golfdynamics.com",
    "graysonsbdc.org",
    "gurssconstruction.com",
    "heartofthedesert.com",
    "highlandparkvillageamarillo.com",
    "hogbait.com",
    "hpa4u.com",
    "hubcityav.com",
    "iaedonline.com",
    "insurancestoptexas.com",
    "integrityoverheaddoor.com",
    "jaredblankenship.com",
    "kalscoops.com",
    "kimrad.com",
    "kmocfm.com",
    "kyliehinermemorialplayground.com",
    "ladybuginc.net",
    "lawfirmrlt.com",
    "lonestarconstruction.com",
    "lonestarcreativeproductions.com",
    "lonestarrunnersclub.net",
    "lovell-law.net",
    "mandrliquoronline.com",
    "mathistrans.com",
    "midriverscc.org",
    "midwestmachinellc.com",
    "mollydavismarketing.com",
    "navarrocollegesbdc.org",
    "ncsbdc.org",
    "neatcoaching.com",
    "officecenterinc.com",
    "onechairatatime.org",
    "opportunityplan.com",
    "originalfactoryscent.com",
    "pancakestation.com",
    "panhandleherald.com",
    "panhandleoilmens.org",
    "parissbdc.com",
    "parissbdc.org",
    "patdavisproperties.com",
    "pattersonlawgroup.com",
    "peeplescleaning.com",
    "pizzaplanet.com",
    "plainstransportation.com",
    "premier-alarm.com",
    "randrscales.com",
    "rdad-inc.com",
    "scarabmfg.com",
    "scrappc.com",
    "sgmtexaslaw.com",
    "sister-bear.com",
    "southwestambucs.org",
    "speedsilks.com",
    "srlawtx.com",
    "starlightcanyon.com",
    "susanbarros.com",
    "terrywestercounseling.com",
    "texasbpwfoundation.org",
    "texaspanhandlecenters.org",
    "texaspanhandlecharities.org",
    "themarkandrewsagency.com",
    "theplazarestaurant.com",
    "thesolawfirm.com",
    "todaysmemoriesamarillo.com",
    "traleecrisiscenter.org",
    "tuckerhvac.com",
    "twentyfive20.com",
    "ucidev.com",
    "ucidigital.com",
    "ucidocuments.com",
    "ucishredding.com",
    "ucisupport.com",
    "uciwebware.com",
    "watleyseed.com",
    "wellingtonritztheatre.com",
    "westtexasfresh.com",
    "westtexasrx.com",
    "whaonline.net",
    "williamsboyce.com"
]
# Set timezone to CST
cst = pytz.timezone('America/Chicago')

def convert_utc_to_cst(utc_time):
    """Converts UTC time to CST."""
    return utc_time.astimezone(cst)

def get_ssl_certificate(hostname, port=443):
    """
    Retrieves the SSL certificate for a given hostname and port.
    Returns a dictionary with certificate details.
    """
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                # Parse certificate details
                not_after_str = cert.get('notAfter')
                not_after_iso = None
                if not_after_str:
                    try:
                        not_after = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                        not_after_iso = not_after.isoformat()
                    except ValueError as ve:
                        logger.error(f"Failed to parse notAfter date for {hostname}: {ve}")

                not_before_str = cert.get('notBefore')
                not_before_iso = None
                if not_before_str:
                    try:
                        not_before = datetime.strptime(not_before_str, '%b %d %H:%M:%S %Y %Z')
                        not_before_iso = not_before.isoformat()
                    except ValueError as ve:
                        logger.error(f"Failed to parse notBefore date for {hostname}: {ve}")

                cert_info = {
                    'subject': dict(x[0] for x in cert['subject']) if 'subject' in cert else {},
                    'issuer': dict(x[0] for x in cert['issuer']) if 'issuer' in cert else {},
                    'version': cert.get('version'),
                    'serialNumber': cert.get('serialNumber'),
                    'notBefore': not_before_iso,
                    'notAfter': not_after_iso,
                    'subjectAltName': cert.get('subjectAltName')
                }
                return cert_info
    except Exception as e:
        logger.error(f"Failed to retrieve SSL certificate for {hostname}: {e}")
        return None

def check_for_tags(html_content):
    """
    Checks for Facebook Pixel and Google Analytics tags in the HTML content
    and returns the actual code snippets if found.
    """
    fb_pixel_match = re.search(r'(<script.*?fbq\(\'init\',.*?</script>)', html_content, re.DOTALL)
    ga_tag_match = re.search(r'(<script.*?gtag\(\'config\',.*?</script>)', html_content, re.DOTALL)

    fb_pixel_code = fb_pixel_match.group(1) if fb_pixel_match else None
    ga_tag_code = ga_tag_match.group(1) if ga_tag_match else None

    return fb_pixel_code, ga_tag_code

def check_domain(domain, timeout=10):
    """
    Checks if a domain is up by attempting HTTPS first, then HTTP if HTTPS fails.
    Also retrieves the IP address of the domain, SSL certificate details, 
    and checks for Facebook Pixel and Google Analytics tags.
    """
    url_schemes = ["https://", "http://"]
    result = {
        'is_up': False,
        'response_time': None,
        'status_code': None,
        'last_checked': convert_utc_to_cst(datetime.utcnow()).isoformat(),
        'ip_address': None,
        'ssl_info': None,
        'fb_pixel': False,
        'ga_tag': False,
        'fb_pixel_code': None,  # Store Facebook Pixel code
        'ga_tag_code': None     # Store Google Analytics code
    }

    try:
        result['ip_address'] = socket.gethostbyname(domain)
    except socket.gaierror:
        logger.error(f"Could not retrieve IP address for {domain}")
        result['ip_address'] = "Unknown"

    for scheme in url_schemes:
        url = f"{scheme}{domain}"
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0'})
            response_time = time.time() - start_time
            result.update({
                'is_up': 200 <= response.status_code < 300,
                'response_time': round(response_time, 2),
                'status_code': response.status_code,
                'last_checked': convert_utc_to_cst(datetime.utcnow()).isoformat()
            })

            # Check for Facebook Pixel and Google Analytics tags and store the code
            html_content = response.text
            fb_pixel_code, ga_tag_code = check_for_tags(html_content)
            result['fb_pixel'] = bool(fb_pixel_code)
            result['ga_tag'] = bool(ga_tag_code)
            result['fb_pixel_code'] = fb_pixel_code
            result['ga_tag_code'] = ga_tag_code
            
            break  # Successful check, no need to try other schemes
        except requests.exceptions.SSLError as ssl_err:
            logger.error(f"SSL error when checking {domain}: {ssl_err}")
            cert_info = get_ssl_certificate(domain)
            result['ssl_info'] = cert_info
            break
        except requests.RequestException as e:
            logger.error(f"Failed to check {domain}: {e}")
            continue

    if not result['ssl_info']:
        cert_info = get_ssl_certificate(domain)
        result['ssl_info'] = cert_info

    return result


def perform_monitoring():
    """
    Background monitoring function that updates domain_statuses without yielding.
    Uses a lock to prevent concurrent executions.
    """
    if monitor_lock.locked():
        logger.warning("Monitoring is already in progress. Skipping this cycle.")
        return
    with monitor_lock:
        logger.info("Starting background domain monitoring cycle.")
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_domain = {executor.submit(check_domain, domain): domain for domain in domains}

            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    status = future.result()
                    domain_statuses[domain] = status
                    if status['is_up']:
                        logger.info(f"{domain} is UP. Response Time: {status['response_time']}s, Status Code: {status['status_code']}")
                    else:
                        if status['ssl_info']:
                            ssl_expiry = status['ssl_info'].get('notAfter', 'N/A')
                            logger.warning(f"{domain} is DOWN due to SSL issue. SSL Expiration: {ssl_expiry}")
                        else:
                            logger.warning(f"{domain} is DOWN. Response Time: {status['response_time']}s, Status Code: {status['status_code']}")
                except Exception as exc:
                    logger.error(f"{domain} generated an exception: {exc}")
        logger.info("Background domain monitoring cycle completed.")

def sse_monitor_domains():
    """
    Generator function for SSE that streams domain status updates without performing monitoring.
    """
    logger.info("Starting SSE domain status streaming.")
    while True:
        # Stream the current domain_statuses
        data = json.dumps(domain_statuses)
        yield f"data: {data}\n\n"
        time.sleep(5)
    logger.info("SSE domain status streaming completed.")