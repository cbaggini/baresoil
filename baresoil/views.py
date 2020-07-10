from django.shortcuts import render
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

import ee
import folium
from folium import plugins
import json

from .forms import DateForm, NDVIForm
from .models import PreviousQueries
from .ndvi_calc_ee import get_footprint, get_tile, get_ndvi, get_cloud
from . import params as gee_account

def home(request, newContext = {}):
    form = DateForm()
    invalid_input = ''
    context = {'form': form, 'invalid_input': invalid_input}
    context.update(newContext)
    return render(request, 'baresoil/home.html', context)

def latest(request):
    # get latest five items from database
    qry = PreviousQueries.objects.all().order_by('-request_datetime')[:5]
    d = {}
    i = 1

    # initialise GEE
    credentials = ee.ServiceAccountCredentials(gee_account.service_account, gee_account.private_key)
    ee.Initialize(credentials)
    MONTHS = {'1':'January', '2':"February", '3':'March', '4':'April', '5':'May','6':'June',
        '7':'July', '8': 'August', '9':'September', '10': 'October', '11':'November', 
        '12':'December'}
    # get context for renderer: dates, ndvi values and maps
    for item in qry:
        d["ndvi{0}".format(i)] = ndvi = item.ndvi
        d["ndvi_low{0}".format(i)] = ndvi_low = item.ndvi_low
        mnth = str(item.mnth)
        d["mnth{0}".format(i)] = MONTHS[mnth]
        d["yr{0}".format(i)] = yr = str(item.yr)
        d["request_datetime{0}".format(i)] = item.request_datetime

        nelat = item.nelat
        nelng = item.nelng
        swlat = item.swlat
        swlng = item.swlng

        footprint = get_footprint(nelat,nelng,swlat,swlng)
        tile = get_tile(mnth,yr,footprint) 
        ndvi_vector = get_ndvi(tile,ndvi,ndvi_low, footprint) 
        cloud = get_cloud(tile)

        m = folium.Map()

        map_id_dict2 = ndvi_vector.getMapId({'palette': ['#B22222']})

        folium.TileLayer(
            tiles = map_id_dict2['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = 'Bare soil',
            overlay = True,
            control = True).add_to(m)

        map_id_dict1 = cloud.getMapId({'min':0,'max':1, 'palette': ['#0000FF']})

        folium.raster_layers.TileLayer(
            tiles = map_id_dict1['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = 'Cloud cover',
            overlay = True,
            control = True).add_to(m)

        bbox = folium.vector_layers.Rectangle(
                    [[swlat,swlng],[nelat,swlng],
                    [nelat,nelng],[swlat, swlng],
                    [swlat,swlng]]
                )
        bbox.add_to(m)
        m.fit_bounds(bbox.get_bounds())
        folium.LayerControl().add_to(m)
        mapn=m._repr_html_()
        d["map{0}".format(i)] = mapn
        i += 1
    
    return render(request, 'baresoil/latest.html', d)

def about(request):
    return render(request, 'baresoil/about.html', {'':''})

@csrf_exempt 
def ndvi(request):
    # if user has pressed 'Save' button
    if request.method == 'POST' and 'down' in request.POST:
        ndviform = NDVIForm(request.POST)
        # if layers have been calculated
        if ndviform.is_valid() and ndviform.cleaned_data['calculated'] == 'Yes':
            mnth = ndviform.cleaned_data['mnth']
            yr = ndviform.cleaned_data['yr']
            ndvi = float(ndviform.cleaned_data['ndvi'])
            ndvi_low = float(ndviform.cleaned_data['ndvi_low'])
            nelat = ndviform.cleaned_data['nelat']
            nelng = ndviform.cleaned_data['nelng']
            swlat = ndviform.cleaned_data['swlat']
            swlng = ndviform.cleaned_data['swlng']

            # add row to database
            new_row = PreviousQueries.objects.create(
                mnth = int(mnth),
                yr = int(yr),
                ndvi = ndvi,
                ndvi_low = ndvi_low,
                nelat = nelat,
                nelng = nelng,
                swlat = swlat,
                swlng = swlng
            )
            new_row.save()
            form = DateForm()
            # redirect to homepage with success message
            invalid_input = 'success'
            context = {'form': form, 'invalid_input': invalid_input}
            response = home(request, context)
            return response
        # if area has been selected
        elif ndviform.is_valid():
            invalid_input = 'nocalc'
            mnth = ndviform.cleaned_data['mnth']
            yr = ndviform.cleaned_data['yr']
            ndvi = float(ndviform.cleaned_data['ndvi'])
            ndvi_low = float(ndviform.cleaned_data['ndvi_low'])
            nelat = ndviform.cleaned_data['nelat']
            nelng = ndviform.cleaned_data['nelng']
            swlat = ndviform.cleaned_data['swlat']
            swlng = ndviform.cleaned_data['swlng']
            m = folium.Map()
            bbox = folium.vector_layers.Rectangle(
                [[swlat,swlng],[nelat,swlng],
                [nelat,nelng],[swlat, swlng],
                [swlat,swlng]]
            )
            bbox.add_to(m)
            m.fit_bounds(bbox.get_bounds())
            ndvi_map=m._repr_html_()
            return render(request, 'baresoil/ndvi.html', {'ndviform': ndviform, 
            'invalid_input': invalid_input, 'ndvi_map': ndvi_map})
        # if user presses save without selecting date and area
        else:
            ndviform = NDVIForm()
            m = folium.Map(location=[55, -4],zoom_start=5)
            ndvi_map=m._repr_html_()
            invalid_input = 'noNDVI'
            return render(request, 'baresoil/ndvi.html', {'ndviform': ndviform, 'ndvi_map': ndvi_map,
            'invalid_input': invalid_input})
    # if user has pressed calculate button
    elif request.method == 'POST' and 'calc' in request.POST:
        # set variables
        form = NDVIForm(request.POST)
        if form.is_valid():
            mnth = form.cleaned_data['mnth']
            yr = form.cleaned_data['yr']
            nelat = form.cleaned_data['nelat']
            nelng = form.cleaned_data['nelng']
            swlat = form.cleaned_data['swlat']
            swlng = form.cleaned_data['swlng']
            ndvi = float(form.cleaned_data['ndvi'])
            ndvi_low = float(form.cleaned_data['ndvi_low'])
            calculated = form.cleaned_data['calculated']

            # get footprint and satellite image
            footprint = get_footprint(nelat,nelng,swlat,swlng)
            tile = get_tile(mnth,yr,footprint)            

            # if there is data available
            if tile:
                calculated = 'Yes'
                data = {'mnth': mnth, 'nelat': nelat, 'nelng': nelng, 
                'swlat': swlat, 'swlng': swlng, 'yr': yr, 'ndvi': ndvi, 'ndvi_low': ndvi_low,
                'calculated': calculated}
                ndviform = NDVIForm(initial=data)

                # calculate bare soil and cloud mask layers, plot them on the map
                m = folium.Map()
                ndvi_vector = get_ndvi(tile,ndvi,ndvi_low, footprint) 
                cloud = get_cloud(tile)

                vis_paramsTCI = {
                    'bands': ['B4', 'B3', 'B2'],
                    'min': 0, 'max': 3000}

                map_id_dict = ee.Image(tile).getMapId(vis_paramsTCI)

                folium.raster_layers.TileLayer(
                    tiles = map_id_dict['tile_fetcher'].url_format,
                    attr = 'Google Earth Engine',
                    name = 'Image',
                    overlay = True,
                    control = True
                    ).add_to(m)

                map_id_dict2 = ndvi_vector.getMapId({'palette': ['#B22222']})

                folium.TileLayer(
                    tiles = map_id_dict2['tile_fetcher'].url_format,
                    attr = 'Google Earth Engine',
                    name = 'Bare soil',
                    overlay = True,
                    control = True
                    ).add_to(m)

                map_id_dict1 = ee.Image(cloud).getMapId({'min':0,'max':1, 'palette': ['#0000FF']})

                folium.raster_layers.TileLayer(
                    tiles = map_id_dict1['tile_fetcher'].url_format,
                    attr = 'Google Earth Engine',
                    name = 'Cloud cover',
                    overlay = True,
                    control = True
                    ).add_to(m)

                # create bounding box and zoom map to it
                bbox = folium.vector_layers.Rectangle(
                    [[swlat,swlng],[nelat,swlng],
                    [nelat,nelng],[swlat, swlng],
                    [swlat,swlng]]
                )
                bbox.add_to(m)
                m.fit_bounds(bbox.get_bounds())
                folium.LayerControl().add_to(m)
                ndvi_map=m._repr_html_()

                return render(request, 'baresoil/ndvi.html', {
                    'ndviform': ndviform,
                    'ndvi_map': ndvi_map})
            # if no data is available
            else:
                dateform = DateForm()
                invalid_input = 'nodata'

                return render(request, 'baresoil/home.html', {'dateform': dateform, 
                'invalid_input': invalid_input})
        # if no valid NDVI values
        else:
            mnth = form.fields['mnth']
            yr = form.fields['yr']
            nelat = form.fields['nelat']
            nelng = form.fields['nelng']
            swlat = form.fields['swlat']
            swlng = form.fields['swlng']
            invalid_input = 'noNDVI'
            m = folium.Map(
            location=[55, -4],
            zoom_start=5
            )
            ndvi_map=m._repr_html_()
            data = {'mnth': mnth, 'nelat': nelat, 'nelng': nelng, 
            'swlat': swlat, 'swlng': swlng, 'yr': yr}
            ndviform = NDVIForm(initial=data)
            return render(request, 'baresoil/ndvi.html', {'ndviform': ndviform, 
            'invalid_input': invalid_input, 'ndvi_map': ndvi_map})
    # if user gets to page from "select area" page
    elif request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            mnth = form.cleaned_data['mnth']
            yr = form.cleaned_data['yr']
            nelat = form.cleaned_data['nelat']
            nelng = form.cleaned_data['nelng']
            swlat = form.cleaned_data['swlat']
            swlng = form.cleaned_data['swlng']

            # populate ndvi form and zoom to area of interest
            data = {'mnth': mnth, 'nelat': nelat, 'nelng': nelng, 
            'swlat': swlat, 'swlng': swlng, 'yr': yr}
            ndviform = NDVIForm(initial=data)
            m = folium.Map(
                location=[55, -4],
                zoom_start=5
            )
            bbox = folium.vector_layers.Rectangle(
                [[swlat,swlng],[nelat,swlng],
                [nelat,nelng],[swlat, swlng],
                [swlat,swlng]]
            )
            bbox.add_to(m)
            m.fit_bounds(bbox.get_bounds())
            ndvi_map=m._repr_html_()
            return render(request, 'baresoil/ndvi.html', {'mnth': mnth, 'nelat': nelat, 'nelng': nelng, 
            'swlat': swlat, 'swlng': swlng, 'yr': yr, 'ndviform': ndviform, 'ndvi_map': ndvi_map})
        # if area has not been selected
        else:
            form = DateForm()
            invalid_input = 'noarea'
            return render(request, 'baresoil/home.html', {'form': form, 'invalid_input': invalid_input 
            })
    # getting to page with GET request
    else:
        ndviform = NDVIForm()
        m = folium.Map(
            location=[55, -4],
            zoom_start=5
        )
        ndvi_map=m._repr_html_()
        return render(request, 'baresoil/ndvi.html', {'ndviform': ndviform, 'ndvi_map': ndvi_map})
