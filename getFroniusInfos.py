import requests_openapi

c = requests_openapi.Client()
c.load_spec_from_file("./solarApiv1.json")

resp = c.GetInverterRealtimeData({"DeviceClass":"Inverter"}) # resp: requests.Response
resp.json()
