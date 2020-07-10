This Django website uses Sentinel2 satellite images processed with Google Earth Engine to estimate bare soil presence in an user-selected area and date. 
The Sentinel2 level-2A that this website uses show atmospherically corrected surface reflectance with 10 metres resolution.
They are available since March 2018 for most of Europe, and since December 2018 for the rest of the world.

On the home page, the user can select a month and year and an area of interest. A three-month time range centered on the selected month will be searched for images
with cloud cover lower than 30%. If images are available, the system will produce a bare soil layer based on a user-selected Normalised Difference Vegetation Index (NDVI) range.
The bare soil layer potential area is determined by selecting the classes "bare soil" and "vegetation" pixels in the SCL (scene classification) band and then only selecting the 
pixels in the selected NDVI range. A cloud mask layer is produced by selecting the cloud and cirrus masks in the QA band.

The user can save the parameters of the request to the website database, and the latest five saved queries will be shown in the "Latest items" page.

Demo at https://tranquil-falls-73463.herokuapp.com/home/


