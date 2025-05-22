import requests
from requests_ntlm import HttpNtlmAuth

# Target WinRM endpoint
url = 'http://10.1.1.6:5985/wsman'
username = 'test'
password = 'test'

# WinRM SOAP envelope for running a simple command
command = "whoami"
soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:w="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd">
  <s:Header>
    <a:To>{url}</a:To>
    <w:ResourceURI s:mustUnderstand="true">http://schemas.microsoft.com/powershell/Microsoft.PowerShell</w:ResourceURI>
    <a:ReplyTo>
      <a:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</a:Address>
    </a:ReplyTo>
    <a:Action s:mustUnderstand="true">http://schemas.xmlsoap.org/ws/2004/09/transfer/Create</a:Action>
    <w:MaxEnvelopeSize s:mustUnderstand="true">153600</w:MaxEnvelopeSize>
    <a:MessageID>uuid:12345678-1234-5678-1234-567812345678</a:MessageID>
    <w:OperationTimeout>PT60S</w:OperationTimeout>
    <w:Locale xml:lang="en-US" s:mustUnderstand="false" />
    <w:DataLocale xml:lang="en-US" s:mustUnderstand="false" />
    <p:SessionId>uuid:00000000-0000-0000-0000-000000000000</p:SessionId>
  </s:Header>
  <s:Body>
    <p:CommandLine xmlns:p="http://schemas.microsoft.com/wbem/wsman/1/windows/shell">
      <p:Command>{command}</p:Command>
    </p:CommandLine>
  </s:Body>
</s:Envelope>
"""

# Make the request using NTLM authentication
try:
    response = requests.post(
        url,
        data=soap_envelope,
        headers={'Content-Type': 'application/soap+xml;charset=UTF-8'},
        auth=HttpNtlmAuth(f'hackad.com\\{username}', password),
        verify=False
    )

    if response.status_code == 200:
        print("[+] Command executed successfully")
        print(response.text)
    else:
        print(f"[!] Error: HTTP {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"[!] Exception: {e}")
