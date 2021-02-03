<p align="center">

  <h3 align="center">Bare soil calculator</h3>

  <p align="center">
    Django app to calculate potential areas of bare soil analysing Sentinel2 satellite imagery with Google Earth Engine.
  </p>
</p>



<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)


<!-- ABOUT THE PROJECT -->
## About The Project

<p>This Django website uses Sentinel2 satellite images processed with Google Earth Engine to estimate bare soil presence in an user-selected area and date. 
The Sentinel2 level-2A that this website uses show atmospherically corrected surface reflectance with 10 metres resolution.
They are available since March 2018 for most of Europe, and since December 2018 for the rest of the world.</p>

<p>On the home page, the user can select a month and year and an area of interest. A three-month time range centered on the selected month will be searched for images
with cloud cover lower than 30%. If images are available, the system will produce a bare soil layer based on a user-selected Normalised Difference Vegetation Index (NDVI) range.
The bare soil layer potential area is determined by selecting the classes "bare soil" and "vegetation" pixels in the SCL (scene classification) band and then only selecting the 
pixels in the selected NDVI range. A cloud mask layer is produced by selecting the cloud and cirrus masks in the QA band.</p>

<p>The user can save the parameters of the request to the website database, and the latest five saved queries will be shown in the "Latest items" page.</p>
<p>The app needs to be connected to a local or remote instance of a PostGIS database.</p>
<p>Demo at https://tranquil-falls-73463.herokuapp.com/home/</p>

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Python >= 3.7<br>

A PostGIS database<br>

A Google Earth Engine API key ([instructions on how to get one here](https://developers.google.com/earth-engine/guides/app_key))


### Installation

1. Clone the repo
```sh
git clone https://github.com/cbaggini/baresoil.git
```
2. Install the necessary Python packages
```sh
pip install requirements.txt
```
3. Add settings.py to the geodjango folder.  

<!-- USAGE EXAMPLES -->
## Usage

#### Home page

Here the user can select the month they want to get data for and draw the area of interest on a map.<br>
Clicking "Next" will redirect them to the calculation page.
![alt text](https://github.com/cbaggini/baresoil/blob/master/home.png?raw=true)

#### Calculation page

Here the user automatically zooms to the area they selected in the previous page and decide which range of Normalised Vegetation Difference Index (NDVI) is likely to indicate potential bare soil.<br>
Clicking "Calculate" will perform the calculations on Google Earth Engine and will add three layers to the map: satellite imagery, potential bare soil (red) and cloud cover, where the calculation could not be performed (blue).<br>
The calculation can be repeated many times with different values until the user is happy with the result <br>
Clicking "Save" will save the request into the database.

![alt text](https://github.com/cbaggini/baresoil/blob/master/ndvi.png?raw=true)

#### Latest items

Here the user can visualise the latest five queries that have been saved to the database.<br>
![alt text](https://github.com/cbaggini/baresoil/blob/master/latest.png?raw=true)
