import requests
import hashlib
from urllib import parse
import my_config
import json
import urllib

password1 = my_config.password1
password2 = my_config.password2

merchant_login = my_config.merchant_login


def calculate_signature(*args) -> str:
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def sucker(amount, description, invoice_id):
    receipt_data = {"items": [{"name": description, "quantity": 1, "sum": amount, "tax": "none"}]}

    receipt = json.dumps(receipt_data)
    receipt_urlencode = urllib.parse.quote(receipt)
    crc_str = f"{merchant_login}:{amount}:{invoice_id}:{receipt}:{password1}"
    crc = hashlib.md5(crc_str.encode()).hexdigest()

    url = (f"https://auth.robokassa.ru/Merchant/Index.aspx?MrchLogin={merchant_login}&"
           f"OutSum={amount}&InvId={invoice_id}&Receipt={receipt_urlencode}&"
           f"Desc={description}&SignatureValue={crc}")
    
    return url


def generate_payment_link2(amount, description, invoice_id):
    receipt = json.dumps({"items": [{"name": description, "quantity": 1, "sum": amount, "tax": "none"}]})
    receipt_urlencode = urllib.parse.quote(receipt)
    signature = calculate_signature(merchant_login, amount, invoice_id, receipt, password1)
    data = {'MerchantLogin': merchant_login, 'OutSum': amount, 'InvId': invoice_id, 'Receipt': receipt_urlencode, 'Description': description,
            'SignatureValue': signature, 'IsTest': my_config.test_payment}
    return f'https://auth.robokassa.ru/Merchant/Index.aspx?{parse.urlencode(data)}'


def generate_payment_link(amount, description, invoice_id):
    pre_data = parse.urlencode({"items":[{"name": description, "quantity": 1, "sum": amount, "tax": "none"}]})
    signature = calculate_signature(merchant_login, amount, invoice_id, pre_data, password1)
    data = {'MerchantLogin': merchant_login, 'OutSum': amount, 'InvId': invoice_id, 'Description': description, 'SignatureValue': signature, 'IsTest': my_config.test_payment}
    return f'https://auth.robokassa.ru/Merchant/Index.aspx?{parse.urlencode(data)}'


def check_payment_status(invoice_id):
    signature_str = f"{merchant_login}:{invoice_id}:{password2}"
    signature = hashlib.md5(signature_str.encode()).hexdigest()
    request_link = f'https://auth.robokassa.ru/Merchant/WebService/Service.asmx/OpStateExt?MerchantLogin={merchant_login}&InvoiceID={invoice_id}&Signature={signature}'
    response = requests.post(request_link)
    return extract_code_from_xml(response.text), request_link


def extract_code_from_xml(xml_data):
    parts = xml_data.split("<Code>")
    if len(parts) > 2: return int(parts[2].split("</Code>")[0])
    else: return -1


print(generate_payment_link2(15, 'asdasd', 225))