import json
import urllib.request
import uuid
import hmac
import hashlib

def momo(amount):
    #thanh toan momo test
    #parameters send to MoMo get get payUrl
    endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
    partnerCode = "MOMOBKUN20180529"
    accessKey = "klm05TvNBzhg7h7j"
    secretKey = "at67qH6mk8w5Y1nAyMoYKMWACiEi2bsa"
    orderInfo = "Thanh toán đơn hàng"
    redirectUrl = "http://127.0.0.1:5000/returnmomo"
    ipnUrl = "http://127.0.0.1:5000/notimomo"
    amount = str(amount)
    orderId = str(uuid.uuid4())
    requestId = str(uuid.uuid4())
    requestType = "captureWallet"
    extraData = "" #pass empty value or Encode base64 JsonString

    #before sign HMAC SHA256 with format: accessKey=$accessKey&amount=$amount&extraData=$extraData&ipnUrl=$ipnUrl&orderId=$orderId&orderInfo=$orderInfo&partnerCode=$partnerCode&redirectUrl=$redirectUrl&requestId=$requestId&requestType=$requestType
    rawSignature = "accessKey="+accessKey+"&amount="+amount+"&extraData="+extraData+"&ipnUrl="+ipnUrl+"&orderId="+orderId+"&orderInfo="+orderInfo+"&partnerCode="+partnerCode+"&redirectUrl="+redirectUrl+"&requestId="+requestId+"&requestType="+requestType
    #signature
    h = hmac.new(bytes(secretKey, 'utf-8'), bytes(rawSignature, 'utf-8'), hashlib.sha256)
    signature = h.hexdigest()
    #json object send to MoMo endpoint
    data = {
            'partnerCode' : partnerCode,
            'partnerName' : "Test",
            'storeId' : "MomoTestStore",
            'requestId' : requestId,
            'amount' : amount,
            'orderId' : orderId,
            'orderInfo' : orderInfo,
            'redirectUrl' : redirectUrl,
            'ipnUrl' : ipnUrl,
            'lang' : "vi",
            'extraData' : extraData,
            'requestType' : requestType,
            'signature' : signature
    }
    data = json.dumps(data)
    clen = len(data)
    req = urllib.request.Request(endpoint, data.encode('utf-8'), {'Content-Type': 'application/json', 'Content-Length': clen})
    f = urllib.request.urlopen(req)
    response = f.read()
    f.close()
    return {
            'payUrl' : json.loads(response)['payUrl'],
            'requestId' : requestId,
            'amount' : amount,
            'orderInfo' : orderInfo,
            'orderId': orderId,
            'partnerCode' : partnerCode,
    }