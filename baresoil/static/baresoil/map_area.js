// draw map
var map = L.map('map_area', {
    center: [55, -4],
    zoom: 5
});

// Set up the OSM layer
L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: 'Data © <a href="http://osm.org/copyright">OpenStreetMap</a>',
      maxZoom: 18
}).addTo(map);

// add editable layers
var editableLayers = new L.FeatureGroup();
map.addLayer(editableLayers);

// define drawing toolbar options
var options = {
  position: 'topleft',
  draw: {
      polyline: false,
      polygon: false,
      circle: false,
      rectangle: true,
      marker: false
  }
};

// add drawing toolbar
var drawControl = new L.Control.Draw(options);
map.addControl(drawControl);

// when the user starts drawing, clear previous polygons
map.on('draw:drawstart', function(e) {

  editableLayers.clearLayers();
});

// add drawn polygon to editable layers
map.on('draw:created', function(e) {
  layer = e.layer;
  
  editableLayers.addLayer(layer);
  
  let areaform = document.getElementById("areaform");
  areaform.nelat.value = layer._bounds._northEast.lat;
  areaform.nelng.value = layer._bounds._northEast.lng;
  areaform.swlat.value = layer._bounds._southWest.lat;
  areaform.swlng.value = layer._bounds._southWest.lng;
  
});

