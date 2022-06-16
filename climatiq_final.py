import requests, json, time, os, decimal
from decimal import Decimal
tenant = '<tenant>'
key = '<key>'

def get_clim_data(clim_rqst_val, entityid):
  global tenant
  rqst_clim_uri = "https://beta3.api.climatiq.io/estimate"
  rqst_key = "<key>"
  rqst_clim_cpu = "cpu-provider_azure-region_east_us"
  rqst_number = clim_rqst_val
  #rqst_number = 2
  rqst_time = 1
  rqst_time_unit = "m"

  payload = '{"emission_factor":'+f'"{rqst_clim_cpu}",' \
      +'"parameters":' \
      +'{"number":' +f'{rqst_number},' \
      +'"time":' +f'{rqst_time},' \
      +'"time_unit":' +f'"{rqst_time_unit}"' \
      +'}}' 

  clim_rqst = requests.post(rqst_clim_uri, headers={"Content-Type":"application/json","Authorization":f"Bearer {rqst_key}"}, data=payload) 
  #print(type(clim_rqst))
  jresponse = clim_rqst.json()
  #jresponse = json.load(clim_rqst)


  #print(type(jresponse))
  #print(json.dumps(jresponse, indent=2))
  clim_co2e = jresponse['co2e']
  clim_co2e_rnd = f"{clim_co2e:8f}"
  #print(clim_co2e_rnd)
  #print(type(clim_co2e_rnd))
  clim_co2e_rndmg = float(clim_co2e_rnd) * 1000000
  #print(clim_co2e_rndmg)

  payload = f'host.co2etest2,dt.entity.host={entityid} {clim_co2e_rndmg}'
  #print(payload)

  metric_ingest_end = f'{tenant}/api/v2/metrics/ingest'

  #print(metric_ingest_end)
  post_data_uri = requests.post(metric_ingest_end, headers={"Content-Type":"text/plain","Authorization":f"Api-Token {key}"}, data=payload) 
  #print(post_data_uri)


def get_host_deets(entityid):
    global tenant
    global key

    host_deets_url =f'{tenant}/api/v2/entities/{entityid}?format=json&api-token={key}'
    response = requests.get(host_deets_url)
    jresponse = response.json()
    #print(json.dumps(jresponse, indent=2))
    #print(entityid)
    host_state = jresponse['properties']['state']
    host_cloudtype = jresponse['properties']['cloudType']
    host_memtotal = jresponse['properties']['memoryTotal']
    host_cpucores = jresponse['properties']['cpuCores']
    host_lcpucores = jresponse['properties']['logicalCpuCores']
    clim_rqst_val=host_lcpucores
    #print(clim_rqst_val)
    #print(host_state, host_cloudtype, host_cpucores, host_lcpucores, host_memtotal)
    get_clim_data(clim_rqst_val,entityid)
    

#PROGRAM STARTS
entity_type = 'HOST'
entity_type_uri =f'{tenant}/api/v2/entities?format=json&api-token={key}&entitySelector=type("{entity_type}")'

#nextcursor_get_events_url = f'{tenant}{url}?format=json&api-token={key}'
response = requests.get(entity_type_uri)
jresponse = response.json()
#print(jresponse)

#print(json.dumps(jresponse, indent=2))
all_entityids = jresponse['entities']
#print(all_entityids)

#debug or for json meta
#host1 = 'HOST-3B6460236B8814E4'
#get_host_deets(host1)

for record in all_entityids:
    
    entityid = record['entityId']
    #print(entityid)
    get_host_deets(entityid)