from django.shortcuts import render
import folium 
import json 
import ee 
import time 
from . import L8
from . import precipitation as pt
from . import landsat
from . import VHI as vh
from colorama import init, Fore, Style

init()

# Create your views here.
json_data = '''
{
  "type": "service_account",
  "project_id": "ee-muthamijohn",
  "private_key_id": "ba887a502e5b94d1c484429fb58de81fda8bf013",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnBlXhl3LS4NDO\nO/32iManSz+kH+YFYfjqTIutkj+JUJ2CVywYIB85cJVGbQ0k23SVS1kx0wrhlA+b\nBzDwtsVBFev4/w6NeZ/YeqL4U/Ky9SP7t6wAmdDkijP9/EtP5IonxuVLYC5trGtw\nL5z6nWgfub0O+A6oTee1bdc3VSlgjt/wKcJwsHFMIr/Brg0lf3chwkBRh0+X1Ntd\np1l1hQVQCshLs32PoDds6ep3cEOpIf/X7diTT1uvprEPUQlNsQf4RzxPBvvqyRZb\nPo1Zv1JO+BAHntC8Z2L3aPmqot9Bq94BqLZm+pRzusoCRJ/Pe+V8J66rM1gR3jup\nEwI3K6abAgMBAAECggEABp5+DmY9sXtU8XdeXyplRQGUahRH8PREmw4H7KVpFmLQ\nrl1DoBXvZtiK8eZZQpnePhrLh0/0lG/7r/C4ncsaEhqksvkL28tzUqIf9A6cbAv1\nYYDFgXIwqkq+OLu9q4YRFSmqsjJp/jd6ooPtVd+hd4n/otvUKOAj5WrCJq03UJFu\n8NEP2aVF4OiVjYLhN5DaN1I+b7lsAA88ZcAYDYxOKiRvkIEyD2S3lJg46+cfIRKz\nbuNV65tWDsDWQL9djB8bRgmUnXjFmEfjiBxWyqv4JF2Xs4/bEuPmX3u06Zfy9UqE\nt/lhvXQ/s0Ou6ayrbDN7jd8yJuIl8EBDQAF6BWGSwQKBgQDWaroZc75ETtBEU401\nU8iBBSKI4YLY4RTvbCeaKBcmNGLzqk0nIdX4NxOwMm8P1LiDYJeOcKkxNTB05lNz\n526MomJ7rHx+vFjpi2a068+FuxczmVeEIbgDM8e2jttBjh6PauUxHEbcOsd7k2Je\nunDCHDUjjaCdRaMrWRT7m+qXywKBgQDHarRQ1pdNxmTjeAVyw1s8br6coVrL94Za\nPfBo6eFDcfsrPOdx7iq1NFuoOCWwZm1hBqhWJYWNqwbVS+G4ESaqnTY5LZTzR67X\n2LobeV/ZegpU7KWBt8Pes4ksMQZedNXuQmtZuKpNEXdAV5WKDgPeSIhdLNdevFJf\n99cv/8sycQKBgQCHy3wlVnpwBII+Y7QQzAk2PSxMCJa4CIUbxSGnrjBLD+6DZ54J\nZJKA61DazHYuToi1G92gZpWhBpCz2JON2krXYpiAvxLxqROehZz8hEQf7AebtEgK\n9Nf3nzmi0wLll76fEhIpckEmhUuFZihs2iNDrF2zMKVCNbJLZ9W0LGD81QKBgGEC\nzdmNq2mQnD/0gWIFG3tYvK3h6RPUxK1d+HhxXr660l+Eb2uDW49vey9osR0RlyBe\nZsIR2tjCXL6i/ZnX7iGN/XTvcciwFKS4sEDxWOmpbyFFRnbGeSj72j1/VAPbfr87\n3JF3PpHjb0oD0aGpk8QtMPly+QsDPmelYC/flnBhAoGBALqZ13BjABwBTKimTcmC\nQiI7LvdsAAdO9k4LjSKKSmCyUTAN4hCc5gqKPVxv62ao+rxbHzRqGNvouXePVb8z\nZbXzfXrWLJxci43wkq3UOoB3t5DTkTGQQveD1tFiVFwLrVZUahoDCerMSQRo449s\n1hx46+u8FvPA57M640V7arV8\n-----END PRIVATE KEY-----\n",
  "client_email": "kenya-environmental-dashboard@ee-muthamijohn.iam.gserviceaccount.com",
  "client_id": "101824526217381631179",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kenya-environmental-dashboard%40ee-muthamijohn.iam.gserviceaccount.com"
}
'''

# Preparing values
json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)
#Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

# Add the method to the folium Map class
folium.Map.add_ee_layer = add_ee_layer

def index(request):
    # Create a map centered at Nakuru, Kenya
    m = folium.Map(location=[-2.3746, 37.9715],tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)', zoom_start=9,height='95%',name='terrainOSM')
    worldImagery= folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr= 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',name='ESRI world Imagery')
    # basemapOSM =folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)')
   
    worldImagery.add_to(m)
    # basemapOSM.add_to(m)
    # m.save("../templates/map.html")
    
    # Define the area of interest (AOI) as a shapefile
    geometry = ee.FeatureCollection('projects/ee-muthamijohn/assets/arthi-galana')

    def maskS2clouds(image):
        return image.updateMask(image.select('QA60').eq(0));
    


    YEAR_START = 2016
    YEAR_END = 2022

    startMonth = 1
    endMonth = startMonth


    # Visualization Palette
    # vis = ['d7191c', 'fdae61', 'ffffc0', 'a6d96a', '1a9641']
    vis = ['red','yellow','green']

    # get image from the landsat class in the landsat module 
    landsat8 = landsat.landsat(YEAR_START,YEAR_END,startMonth,endMonth,"LANDSAT/LC08/C02/T1_L2")

    landsatImage=landsat8.getImage()
    dataset = L8.getImageL8(YEAR_START,YEAR_END,startMonth,endMonth)
    ndviL8 = L8.getNDVI(YEAR_START,YEAR_END,startMonth,endMonth)
    precipitation = pt.precipitation(YEAR_START,YEAR_END,startMonth,endMonth) 
    lst = landsat8.calcLSTL8("LANDSAT/LC08/C02/T1",ndviL8,geometry,YEAR_START,YEAR_END,startMonth,endMonth).clip(geometry)
        # Load Sentinel-2 data for the region of interest
    sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filter(ee.Filter.calendarRange(YEAR_START,YEAR_END, 'year')).filter(ee.Filter.calendarRange(startMonth, endMonth, 'month'))\
        .filterBounds(geometry)\
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',5))\
        .map(maskS2clouds).median().clip(geometry)

    # Calculate NDVI
    ndvi = sentinel2.normalizedDifference(['B8', 'B4'])

    # Define visualization parameters for NDVI
    ndvi_vis_params = {
        'min': 0,
        'max': 1,
        'palette': ['red', 'yellow', 'green']
    }

    
    image = landsat8.dataset().median()
    
    VHI,VCI, TCI = vh.getVHI(image,'SR_B5','SR_B4',geometry,lst)
    

    # VHI classification into classes based on threshold values to calculate Drought Index
    image02 = VHI.lt(0.1).And(VHI.gte(-1))
    image04 = ((VHI.gte(0.1)).And(VHI.lt(0.2))).multiply(2)
    image06 = ((VHI.gte(0.2)).And(VHI.lt(0.3))).multiply(3)
    image08 = ((VHI.gte(0.3)).And(VHI.lt(0.4))).multiply(4)
    image10 = (VHI.gte(0.4)).multiply(5)
    Drought_Index = (image02.add(image04).add(image06).add(image08).add(image10)).float()
    Drought_Index_Mean = Drought_Index.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, bestEffort=True,scale=30)





    # todo turn all the image collections to dataframes 
    # def compute_veg_indices(date):
    #     with st.spinner("calculating.This might take a while..."):
    #                 # Compute mean vegetation indices
    #                 ndvi_mean = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
    #                 sarvi_mean = sarvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
    #                 gci_mean = gci.reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
    #                 npcri_mean = npcri.reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
    #                 rvi_mean = rvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)
    #                 evi_mean = evi.reduceRegion(reducer=ee.Reducer.mean(), geometry=ROI1, scale=10)

    #                 mean_ndvi = ee.Number(ndvi_mean.get('nd')).float().getInfo()
    #                 mean_sarvi = ee.Number(sarvi_mean.get('SARVI')).float().getInfo()
    #                 mean_gci = ee.Number(gci_mean.get('GCI')).float().getInfo()
    #                 mean_npcri = ee.Number(npcri_mean.get('NPCRI')).float().getInfo()
    #                 mean_rvi = ee.Number(rvi_mean.get('RVI')).float().getInfo()
    #                 mean_evi = ee.Number(evi_mean.get('EVI')).float().getInfo()
    #                 return {'date': date.format('YYYY-MM-dd').getInfo(), 'mean_ndvi': mean_ndvi,'mean_sarvi':mean_sarvi,'mean_gci': mean_gci,'mean_npcri': mean_npcri,'mean_rvi':mean_rvi,'mean_evi':mean_evi}

    #     # Map the function over a list of dates and convert the resulting list of dictionaries to a pandas dataframe
    #     dates = ee.List(s2.distinct('system:time_start').aggregate_array('system:time_start')).map(lambda time_start: ee.Date(time_start).format('YYYY-MM-dd')).getInfo()
    #     data = [compute_veg_indices(date)for date in dates]
    #     df_all = pd.DataFrame(data).set_index('date')


    #     st.dataframe(df_all, use_container_width=True)

    #  todo land use land cover 


    visualization = {
        'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
        'min': 1,
        'max': 65455,
        'gamma': 1.4,
    }
    
    ndvi_params = {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}


    # Add the layer to the map
    start = time.time()
    # TCI display to map
    m.add_ee_layer(TCI, {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'TCI')
    # # VCI display to map
    m.add_ee_layer(VCI.clip(geometry), {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'VCI')
    # # VHI display to map
    m.add_ee_layer(VHI, {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'VHI')
    # # Drought display to map
    m.add_ee_layer(Drought_Index, {'min': 1, 'max': 5, 'palette': vis}, 'Drought Index')
    end = time.time()
    rslt = end - start

    if float(rslt) >= 30.00:
       print("major layers load time: " + Fore.RED + str(rslt) + Style.RESET_ALL)
    elif float(rslt) >=20.00:
        print("major layers load time: " + Fore.YELLOW + str(rslt) + Style.RESET_ALL)    
    else:
        print("major layers load time: " + Fore.BLUE + str(rslt) + Style.RESET_ALL)

    m.add_ee_layer(dataset.clip(geometry), visualization, 'True Color (432)')
    start=time.time()
    m.add_ee_layer(lst, {'min': 2,'max': 45,'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
'0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
'3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
'ff0000', 'de0101', 'c21301', 'a71001', '911003' ]},'LST')
    end= time.time()

    minrslt= end - start
    if float(minrslt) >= 20.00:
       print("lst display process finished within " + Fore.RED + str(minrslt) + Style.RESET_ALL)
    else:
        print("lst display process finished within " + Fore.BLUE + str(minrslt) + Style.RESET_ALL)


    m.add_ee_layer(precipitation.first().clip(geometry),{
    'min': 1.0,
    'max': 17.0,
    'palette' : ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000'],
    }, 'Precipitation')

    m.add_ee_layer(ndviL8.clip(geometry),ndvi_params,'NDVI L8')


    # Add the NDVI layer to the map
    m.add_ee_layer(ndvi, ndvi_vis_params, 'NDVI')

    # Add a layer control to the map
    m.add_child(folium.LayerControl())

    # print(ee.Number(Drought_Index.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9).values().get(0)))
    

    context = {'map': m._repr_html_()}

    return render(request, 'map.html', context)