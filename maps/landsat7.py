import pandas as pd
import ee 


class landsat:
    def __init__(self,startYear,endyear,season):
        self.startYear =startYear
        self.endYear = endyear
        self.season = season 

    def calculateDroughtIndex(self):
               
        def maskL5(col):
            # Bits 3 and 5 are cloud shadow and cloud, respectively.
            cloudShadowBitMask = (1 << 3)
            cloudsBitMask = (1 << 5)

            # Get the pixel QA band.
            qa = col.select('QA_PIXEL')

            # Both flags should be set to zero, indicating clear conditions.
            mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
            .And(qa.bitwiseAnd(cloudsBitMask).eq(0))

            return col.updateMask(mask)

        geometry =  ee.FeatureCollection("projects/ee-muthamijohn/assets/arthi-galana")


        start_year = self.startYear
        end_year = self.endYear
        season = self.season

        if season=='1':
            startmonth = 1
            endmonth = 3
        elif season == '2':
            startmonth = 4
            endmonth = 6
        elif season =='3':
            startmonth =7
            endmonth = 9
        elif season == '4':
            startmonth = 10
            endmonth = 12
        else:
            print('No such season, Enter a valid season of 1-4')

        landstcollection = ee.ImageCollection("LANDSAT/LE07/C02/T1") \
            .map(maskL5)\
            .filterBounds(geometry)\
            .filter(ee.Filter.calendarRange(start_year, end_year, 'year')) \
            .filter(ee.Filter.calendarRange(startmonth,endmonth, 'month'))

        # def compute_veg_indices(start_date, end_date):
        #         geometry = ee.FeatureCollection("projects/ee-muthamijohn/assets/arthi-galana")
        #         # Drought_Index=Drought_Index.select('NDVI')
        #         # NDVI_mean = ndviL8.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9)
        #         # NDVI_mean = ee.Number(NDVI_mean.get('NDVI')).float().getInfo()

        def calculate_drought_index(self,geometry, start_date, end_date):
            # Cloud mask
                def maskL5(col):
                        # Bits 3 and 5 are cloud shadow and cloud, respectively.
                        cloudShadowBitMask = (1 << 3)
                        cloudsBitMask = (1 << 5)

                        # Get the pixel QA band.
                        qa = col.select('QA_PIXEL')

                        # Both flags should be set to zero, indicating clear conditions.
                        mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
                        .And(qa.bitwiseAnd(cloudsBitMask).eq(0))

                        return col.updateMask(mask)

                # Load the collection
                col = ee.ImageCollection("LANDSAT/LE07/C02/T1") \
                        .map(maskL5) \
                        .filterDate(start_date, end_date) \
                        .filterBounds(geometry)

                col1 = col.mean().clip(geometry)

                # Image reduction
                image = col.mean()

                # Calculate TOA spectral radiance
                ML = 0.055375
                AL = 1.18243
                TOA_radiance = image.expression('ML * B6 + AL', {
                        'ML': ML,
                        'AL': AL,
                        'B6': image.select('B6_VCID_1')
                })

                # Convert TOA spectral radiance to brightness temperature
                K1 = 607.76
                K2 = 1260.56
                brightnessTemp = TOA_radiance.expression(
                        '(K2 / (log((K1 / L) + 1))) - 273.15', {
                        'K1': K1,
                        'K2': K2,
                        'L': TOA_radiance
                        })


                clippedbrightnessTemp = brightnessTemp.clip(geometry)

                # Median
                ndvi = image.normalizedDifference(['B4', 'B3']).rename('NDVI')
                NDVI_IMAGE = ndvi.clip(geometry)

                # Find the min and max of NDVI
                min_val = ndvi.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).get('NDVI')
                max_val = ndvi.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).get('NDVI')
                min_value = ee.Number(min_val)
                max_value = ee.Number(max_val)

                # Fractional vegetation
                fv = ndvi.subtract(min_value).divide(max_value.subtract(min_value)).pow(2).rename('FV')
                VCI = (ndvi.subtract(min_value)).divide(max_value.subtract(min_value))

                # Emissivity
                a = ee.Number(0.004)
                b = ee.Number(0.986)
                EM = fv.multiply(a).add(b).rename('EMM')

                # Calculate land surface temperature
                landSurfaceTemp = brightnessTemp.expression(
                        '(BT / (1 + (10.60 * BT / 14388) * log(epsilon)))', {
                        'BT': brightnessTemp,
                        'epsilon': EM.select('EMM')
                        })

                # Clip the land surface temperature image to the geometry
                clippedLandSurfaceTemp = landSurfaceTemp.clip(geometry)

                # Find the min and max of LST
                min_v = clippedLandSurfaceTemp.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).values().get(0)
                max_v = clippedLandSurfaceTemp.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).values().get(0)
                min_LST = ee.Number(min_v)
                max_LST = ee.Number(max_v)

                max_LST_1 = ee.Image(max_LST)
                #Obtain TCI
                TCI = max_LST_1.subtract(clippedLandSurfaceTemp).divide(max_LST.subtract(min_LST))

                #Calculate VCI
                VHI = (VCI.multiply(0.5)).add(TCI.multiply(0.5))

                # VHI classification into classes based on threshold values to calculate Drought Index
                image02 = VHI.lt(0.1).And(VHI.gte(-1))
                image04 = ((VHI.gte(0.1)).And(VHI.lt(0.2))).multiply(2)
                image06 = ((VHI.gte(0.2)).And(VHI.lt(0.3))).multiply(3)
                image08 = ((VHI.gte(0.3)).And(VHI.lt(0.4))).multiply(4)
                image10 = (VHI.gte(0.4)).multiply(5)
                Drought_Index = (image02.add(image04).add(image06).add(image08).add(image10)).float()

                return Drought_Index, TCI, VCI, VHI

        Drought_Index, TCI, VCI, VHI = calculate_drought_index(geometry, start_date, end_date)

        # imageVHI =ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filterDate(date,date).filterBounds(geometry).map(maskL8sr).median().clip(geometry)
        # VHI,VCI,TCI = vh.getVHI(imageVHI,'SR_B5','SR_B4',geometry,lst)
        VHI_mean = VHI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
        VHI_mean = ee.Number(VHI_mean.get('NDVI')).float().getInfo()
        TCI_mean = TCI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
        TCI_mean = ee.Number(TCI_mean.get('constant')).float().getInfo()
        VCI_mean = VCI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
        VCI_mean = ee.Number(VCI_mean.get('NDVI')).float().getInfo()
        Drought_Index_mean = Drought_Index.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
        Drought_Index_mean = ee.Number(Drought_Index_mean.get('NDVI')).float().getInfo()

        return {'start_date': start_date, 'end_date': end_date, 'VHI_mean': VHI_mean, 'Drought_index_mean': Drought_Index_mean, 'TCI_mean': TCI_mean, 'VCI_mean': VCI_mean}


    #....................................................#

    # # Plot the line graph using the modified DataFrame
    # plt.figure(figsize=(12, 6))
    # plt.plot(standardized_df['start_date'], standardized_df['Standardized_Drought_Index'], marker='o', label='Standardized_Drought_Index')
    # plt.plot(df1['start_date'], df1['VHI_mean'], label='VHI_mean')
    # plt.plot(df1['start_date'], df1['TCI_mean'], label='TCI_mean')
    # plt.plot(df1['start_date'], df1['VCI_mean'], label='VCI_mean')

    # # Customize the plot
    # plt.xlabel('Date')
    # plt.ylabel('Standardized index mean')
    # plt.title('Athi-Galana Basin mean Drought index Over Time')
    # plt.xticks(rotation=45)
    # plt.grid(True)
    # plt.legend()

    # # Add a horizontal line at y=0 to correspond to the x-axis
    # plt.axhline(y=0, color='black', linestyle='--')

    # # Customize y-axis ticks to show positive and negative values
    # plt.yticks([-1, -0.5, 0, 0.5, 1])

    # plt.tight_layout()
    # plt.show()    