# SHIVER: SHeffield Ice Velocity ExploreR

**SHIVER** is an interactive web application designed for the rapid visualization and extraction of high-resolution ice velocity time series data in West Greenland and on the Antarctica Peninsula. 

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue](https://img.shields.io/badge/frontend-Vue.js%203-4FC08D)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)
![Leaflet](https://img.shields.io/badge/map-Leaflet-e6e600)

## ?? Key Features

* **Multi-Region Support:** Seamlessly switch between Greenland (EPSG:3413) and Antarctica (EPSG:3031) projections.
* **Interactive Mapping:** * View tile-served layers for Ice Speed, Measurement Counts, and Acceleration Trends.
    * Dynamic glacier basin outlines (Antarctica) with zoom-dependent labeling.
    * Ice margins and grounding line overlays.
* **Time-Series Extraction:**
    * **Point & Click:** Instant generation of velocity time series for any location on the ice sheet.
    * **Batch Upload:** Upload Shapefiles, GeoJSON, or KML files to extract data for multiple glaciers simultaneously.
* **Advanced Data Processing:**
    * Toggle between **Raw** and **Filtered** datasets.
    * Customizable **Smoothing Parameters** (Savitzky-Golay filter, Gap filling, Window sizes).
    * Visualize Velocity components (Speed, u, v).
* **Export Capabilities:**
    * Download processed data as CSV (individual) or ZIP (batch).
    * Export high-quality plots as PNGs.

## ??? Technology Stack

### Frontend
* **Framework:** Vue.js 3 (Vite)
* **Mapping:** Leaflet & Vue-Leaflet
* **Visualization:** Plotly.js
* **HTTP Client:** Axios

### Backend
* **Server:** FastAPI (Python)
* **Data Handling:** Xarray, Pandas, Zarr
* **Geospatial:** Rio-tiler (Tile serving), GeoPandas, Shapely
* **Signal Processing:** Scipy (Savgol filter)

