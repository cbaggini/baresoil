import ee
from . import params as gee_account

def get_footprint(nelat,nelng,swlat,swlng):
    # initialise EE
    credentials = ee.ServiceAccountCredentials(gee_account.service_account, gee_account.private_key)
    ee.Initialize(credentials)
    
    # define footprint
    footprint= ee.Geometry.Polygon(
        [[[swlng,swlat],
        [nelng,swlat],
        [nelng,nelat],
        [swlng,nelat]]], None, False
    )
    return footprint

def get_tile(mnth,yr,footprint):
    # define function to mask clouds 
    def maskS2clouds(image):
        qa = image.select('QA60')

        # Bits 10 and 11 are clouds and cirrus, respectively.
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11

        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloudBitMask).eq(0)
        mask = mask.bitwiseAnd(cirrusBitMask).eq(0)

        return image.updateMask(mask)

    # define start and end dates for API request
    if mnth == '01':
        start_date = '-'.join([str(int(yr)-1),'12','01'])
        end_date = '-'.join([yr,str(format(int(mnth)+1,'02d')),'01'])
    elif mnth == '12':
        start_date = '-'.join([yr,str(format(int(mnth)-1,'02d')),'01'])
        end_date = '-'.join([str(int(yr)+1),'01','01'])
    else:
        start_date = '-'.join([yr,str(format(int(mnth)-1,'02d')),'01'])
        end_date = '-'.join([yr,str(format(int(mnth)+1,'02d')),'01'])
    
    #get image collection: filter, mosaic and apply cloud mask
    tile_collection =  (ee.ImageCollection('COPERNICUS/S2_SR').filterDate(start_date, end_date)
                        .filterBounds(footprint).filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',30))
                        .map(maskS2clouds).sort('CLOUD_COVER'))

    # mosaic tile collection to one
    #tiles = tile_collection.reduce(ee.Reducer.median()).clip(footprint)
    tiles = tile_collection.mosaic().clip(footprint)

    #if image is empty, return None
    tile_info = ee.Number(tiles.reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = footprint,
        scale = 10000,
        maxPixels = 1e9
        ))
    try:
        tile_info1 = tile_info.getInfo()
        if tile_info1 == {}:
            return None 
    except:
        return None
    
    return tiles

def get_cloud(tile):
    # produce layer of clouds medium/high probability
    image = tile.select('SCL')
    cloud = image.gt(7).add(image.lt(11))
    cloud = cloud.updateMask(cloud.neq(1))
    return cloud 

def get_ndvi(tile, ndvi, ndvi_low, footprint):
    # mask all pixels that are not vegetation or bare soil
    image = tile.select('SCL')
    cloud = image.gt(3).add(image.lt(6))
    tile = tile.updateMask(cloud.eq(2))

    #calculate NDVI
    nir = tile.select('B8')
    red = tile.select('B4')
    ndvi_raster = nir.subtract(red).divide(nir.add(red)).rename('NDVI')

    # select pixels in user-selected NDVI range
    zones = ndvi_raster.gt(ndvi_low).add(ndvi_raster.gt(ndvi))
    zones = zones.updateMask(zones.neq(0))
    zones = zones.updateMask(zones.neq(2))

    # calculate area of bare soil
    # bare = ee.Number(zones.multiply(ee.Image.pixelArea()).reduceRegion(reducer=ee.Reducer.sum(), 
    #         geometry=footprint, scale=60))

    # bare = round(bare.getInfo()['NDVI']/1000000, 2)
    # print(bare)

    return zones

