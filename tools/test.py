import requests

xml = '''<?xml version="1.0" encoding="big5"?>
<STUREQ>
    <UID>你八七</UID>
        <PASSWORD>abcd1234</PASSWORD>
            <CARDNO>123456</CARDNO>
</STUREQ>'''.encode('big5')

print(xml)

headers = {'Content-Type': 'text/xml', 'charset':'big5'} # set what your server accepts

res = requests.post('http://localhost:3000/seqServices/stuinfoByCardno', data=xml, headers=headers)

print(res.headers)

print(res.text)
