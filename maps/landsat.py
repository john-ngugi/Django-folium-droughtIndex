import ee
import time 

class landsat:
    def __init__(self,startYear,endYear,startMonth,endMonth,imageCollection):
       
       self.startYear=2019
       self.endYear = 2021
       self.startMonth = 1 
       self.endMonth =1
       self.imageCollection = "LANDSAT/LC08/C02/T1_L2"
       
    
    def dataset(self):
        dataset = ee.ImageCollection(self.imageCollection).filter(ee.Filter.calendarRange(self.startYear, self.endYear, 'year')).filter(ee.Filter.calendarRange(self.startMonth, self.endMonth, 'month'))

        return dataset
       
    geometry = ee.FeatureCollection('projects/ee-muthamijohn/assets/arthi-galana')
    

    def maskL8sr(self,image):
            # Select the pixel QA band.
        qa = image.select('QA_PIXEL')
        
        # Define the bitmasks for cloud and cloud shadow.
        cloudBitMask = 1 << 3
        cloudShadowBitMask = 1 << 4
        
        # Create the mask for clear conditions.
        mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
            .And(qa.bitwiseAnd(cloudShadowBitMask).eq(0))
        
        # Apply the mask to the image.
        return image.updateMask(mask)


    def getImage(self):
        dataset = self.dataset().map(self.maskL8sr)
        return dataset.median()
    

    def getNDVI(self,NIR,red):
        # Calculate NDVI
        datasetNdvi= self.dataset().median()
        ndvi = datasetNdvi.normalizedDifference([NIR, red]) 
        return ndvi
    
    def getNDVIInset(self,image):
        # Calculate NDVI
        datasetNdvi= self.dataset().median()
        ndvi = datasetNdvi.normalizedDifference(['SR_B5','SR_B4']) 
        datsetNdvi = datasetNdvi.addBands(ndvi.rename('nd'))
        return datsetNdvi

    def calcLSTL8(self,collection,ndvi,geometry,startYear,endYear,startMonth,endMonth):
        start = time.time()
        col = ee.ImageCollection(collection) \
        .map(self.maskL8sr) \
        .filter(ee.Filter.date(str(startYear)+'-'+str(startMonth)+'-'+'28', str(endYear)+'-'+ str(endMonth)+'-'+'28')) \
        .filterBounds(geometry)

        # image = self.dataset().median()
        # Image reduction
        image = col.mean()

        # Calculate TOA spectral radiance
        ML = 0.0003342
        AL = 0.10000
        Oi = 0.29

        TOA_radiance = image.expression('ML * B10 + AL - Oi', {
            'ML': ML,
            'AL': AL,
            'B10': image.select('B10'),
            'Oi': Oi
        })

        # Convert TOA spectral radiance to brightness temperature
        K1 = 774.8853
        K2 = 1321.0789

        brightnessTemp = TOA_radiance.expression(
            '(K2 / (log((K1 / L) + 1))) - 273.15', {
                'K1': K1,
                'K2': K2,
                'L': TOA_radiance
            })

        # Median
        ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')

        # Find the min and max of NDVI
        min_val = ndvi.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).values().get(0)
        max_val = ndvi.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).values().get(0)
        min_value = ee.Number(min_val)
        max_value = ee.Number(max_val)

        # Fractional vegetation
        fv = ndvi.subtract(min_value).divide(max_value.subtract(min_value)).pow(2).rename('FV')


        # Emissivity
        a = 0.004
        b = 0.986
        EM = fv.multiply(a).add(b).rename('EMM')
       
        # Calculate land surface temperature
        landSurfaceTemp = brightnessTemp.expression(
            '(BT / (1 + (10.60 * BT / 14388) * log(epsilon)))', {
                'BT': brightnessTemp,
                'epsilon': EM.select('EMM')
            })


        end = time.time()
        return landSurfaceTemp
                

    def calcLSTL5L4L7(self,termalBand,ndvi):
        self.dataset()
        # todo landsat4,5,7 LST calculation 




