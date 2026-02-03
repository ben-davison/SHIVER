<template>
  <div class="page-container" :class="{ 'is-global-loading': isUploading }">
    
    <div class="map-wrapper" :class="{ 'show-labels': zoom >= 9 }" :style="{ height: mapHeightPercent + '%' }">
      <l-map 
        ref="map" 
        v-model:zoom="zoom" 
        v-model:center="center" 
        :use-global-leaflet="false" 
        @click="onMapClick"
        @overlayadd="onOverlayAdd"
        @overlayremove="onOverlayRemove"
      >
        <l-control-layers position="topleft"></l-control-layers>
		
		<l-control-scale position="bottomleft" :imperial="false" :metric="true"></l-control-scale>
        
        <l-tile-layer 
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}" 
          layer-type="base" 
          name="Satellite Imagery"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>

        <l-tile-layer
          :url="speedUrl"
          :opacity="0.7"
          layer-type="overlay"
          name="Ice Speed"
          :visible="overlayLayer === 'speed'"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>

        <l-tile-layer
          :url="countUrl"
          :opacity="0.7"
          layer-type="overlay"
          name="Measurement Count"
          :visible="overlayLayer === 'count'"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>
		
        <l-tile-layer
          :url="trendUrl"
          :opacity="0.7"
          layer-type="overlay"
          name="Speed Trend"
          :visible="overlayLayer === 'trend'"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>
		
		<l-tile-layer
			:url="vectorUrl"
			layer-type="overlay"
			name="Flow direction arrows"
			:opacity="1.0"
			:z-index="10" 
			:visible="false"
			:options="{ crossOrigin: 'anonymous' }"
		  ></l-tile-layer>
		
        <l-geo-json 
          v-if="currentRegion === 'Antarctica' && glacierData" 
          :geojson="glacierData"
		  :options-style="outlineStyle"
        ></l-geo-json>
		
		<l-geo-json 
          v-if="currentRegion === 'Antarctica' && glacierNamesData" 
          :geojson="glacierNamesData"
          :options="glacierLabelOptions"
        ></l-geo-json>
		
        <l-circle-marker 
          v-for="point in selectedPoints" :key="point.id" :lat-lng="[point.lat, point.lon]"
          :radius="8" :color="point.color" :fill-color="point.color" :fill-opacity="0.6" :weight="2">
        </l-circle-marker>
		
		<l-layer-group layer-type="overlay" name="Ice Margin" :visible="showMargins">
  
			  <l-geo-json 
				v-if="iceEdgeData" 
				:geojson="iceEdgeData" 
				:options-style="() => iceEdgeStyle"
			  ></l-geo-json>

			  <l-geo-json 
				v-if="currentRegion === 'Antarctica' && groundingLineData" 
				:geojson="groundingLineData" 
				:options-style="() => groundingLineStyle"
			  ></l-geo-json>

		</l-layer-group>
		
      </l-map>
	  
      <div class="legend-container">

        <div class="legend-box" v-if="overlayLayer !== 'none' || isFlowActive">
        
			<div v-if="overlayLayer !== 'none'" class="scalar-legend-group">
				<div v-if="overlayLayer === 'speed'">
				  <h4>Ice Speed (Log Scale)</h4>
				  <div class="legend-bar speed-gradient"></div>
				  <div class="legend-labels">
					<span>1</span>
					<span>10</span>
					<span>100</span>
					<span>{{ maxSpeedLabel }}</span>
				  </div>
				</div>

				<div v-else-if="overlayLayer === 'count'">
				  <h4>Percentage Valid Measurements</h4>
				  <div class="legend-bar viridis-gradient"></div>
				  <div class="legend-labels">
					<span>0</span>
					<span>30</span>
					<span>60</span>
					<span>90</span>
				  </div>
				</div>
		
				<div v-else-if="overlayLayer === 'trend'">
				  <h4>Speed Trend (m/yr<sup>2</sup>)</h4>
				  <div class="legend-bar trend-gradient"></div>
				  <div class="legend-labels">
					<span>{{ minTrendLabel }}</span>
					<span>0</span>
					<span>{{ maxTrendLabel }}</span>
				  </div>
				</div>
			</div>
			
			<div v-if="isFlowActive" class="vector-legend-group">
				<div v-if="overlayLayer !== 'none'" class="legend-separator"></div>
				<h4>Flow Vector Scale</h4>
				
				<div class="vector-row">
				  <svg :width="arrowPixelWidth + 15" height="24" class="vector-arrow-svg">
					 <defs>
					   <marker id="arrowhead" markerWidth="8" markerHeight="6" 
							   refX="7" refY="3" orient="auto">
						 <polygon points="0 0, 8 3, 0 6" fill="#333" />
					   </marker>
					 </defs>
					 
					 <line 
					   x1="0" y1="12" 
					   :x2="arrowPixelWidth" y2="12" 
					   stroke="#333" 
					   stroke-width="2" 
					   marker-end="url(#arrowhead)" 
					 />
				  </svg>
				  <span class="vector-label">{{ vectorScaleLabel }}</span>
				</div>
			</div>
			
			<div v-if="showMargins" style="margin-top: 10px; border-top: 1px solid #ccc; padding-top: 5px;">			  
			  <div class="legend-item">
				<div class="legend-line" style="background: black;"></div>
				<span>Ice Margin</span>
			  </div>

			  <div class="legend-item" v-if="currentRegion === 'Antarctica'">
				<div class="legend-line" style="background: magenta;"></div>
				<span>Grounding Line</span>
			  </div>
			</div>

		</div>
		
	  </div>
	  
      <div class="control-panel">
	  
        <div class="brand-header">
		   <button class="btn-gear" @click="showAdvanced = !showAdvanced" title="Advanced Options">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
            </svg>
          </button>
		  
          <button class="btn-help" @click="showHelp = true" title="Help & Instructions">?</button>
          <h1 class="shiver-title">SHIVER</h1>
          <div class="shiver-subtitle">SHeffield Ice Velocity ExploreR</div>
        </div>
		
		<div v-if="showAdvanced" class="advanced-popup">
          <div class="popup-header">
			  <strong>Advanced Options</strong>
			  
			  <div class="header-actions">
				<button @click="restoreDefaults" class="btn-restore-link">
				  Restore defaults
				</button>
				
				<button @click="showAdvanced = false" class="popup-close">&times;</button>
			  </div>
			</div>
          
		  <div class="opt-section">
            <span class="opt-label">Variables:</span>
            <div class="opt-checks">
               <label v-for="v in availableVars" :key="v">
                 <input type="checkbox" :value="v" v-model="selectedVars" @change="debouncedRefetch"> {{ v.toUpperCase() }}
               </label>
            </div>
          </div>

          <div class="opt-section">
            <span class="opt-label">Processing level:</span>
            <div class="opt-checks">
               <label v-for="q in availableQuality" :key="q">
                 <input type="checkbox" :value="q" v-model="selectedQuality" @change="debouncedRefetch"> {{ q }}
               </label>
            </div>
          </div>
		
		  <hr class="opt-divider">
          <div class="opt-section">
            <span class="opt-label">Smoothing Parameters:</span>
            
            <div class="param-row">
              <label>Max gap fill length days</label>
              <input type="range" v-model.number="smoothingParams.gap" min="1" max="120" class="param-slider">
              <input type="number" v-model.number="smoothingParams.gap" class="param-input" @change="debouncedRefetch">
            </div>

            <div class="param-row">
              <label>Window size days (Points)</label>
              <input type="range" v-model.number="smoothingParams.win_raw" min="1" max="121" step="2" class="param-slider">
              <input type="number" v-model.number="smoothingParams.win_raw" class="param-input" @change="debouncedRefetch">
            </div>

            <div class="param-row">
              <label>Window size days (Line)</label>
              <input type="range" v-model.number="smoothingParams.win_daily" min="1" max="121" step="2" class="param-slider">
              <input type="number" v-model.number="smoothingParams.win_daily" class="param-input" @change="debouncedRefetch">
            </div>

            <div class="param-row">
              <label>Polynomial order</label>
              <input type="range" v-model.number="smoothingParams.poly" min="1" max="5" class="param-slider">
              <input type="number" v-model.number="smoothingParams.poly" class="param-input" @change="debouncedRefetch">
            </div>
          </div>
        </div>


        <div class="panel-section">
          <label>Region:</label>
          <select v-model="currentRegion" @change="switchRegion">
            <option value="Greenland">Greenland</option>
            <option value="Antarctica">Antarctica</option>
          </select>
        </div>
		
		<div class="upload-section">
		  <label class="btn-upload" :class="{ 'is-loading': isUploading }">
			<span v-if="!isUploading">Load Zipped Shapefile</span>
			<span v-else class="spinner"></span>
			<input type="file" @change="handleFileUpload" accept=".zip,.json,.geojson,.kml" hidden :disabled="isUploading">
		  </label>
		</div>
		
        <div class="list-toolbar" v-if="selectedPoints.length > 0">
          <button @click="clearAll" class="btn-clear">Clear All</button>
        </div>

        <div class="points-list" v-if="selectedPoints.length > 0">
          <table>
            <thead><tr><th style="width:30px;">ID</th><th>Lat</th><th>Lon</th><th style="width:30px;"></th></tr></thead>
            <tbody>
              <tr v-for="(point, index) in selectedPoints" :key="point.id">
                <td><span class="color-dot" :style="{backgroundColor: point.color}"></span>{{ index + 1 }}</td>
                <td><input type="number" v-model.number="point.lat" step="0.001" class="coord-input" @change="refreshPointData(point)"></td>
                <td><input type="number" v-model.number="point.lon" step="0.001" class="coord-input" @change="refreshPointData(point)"></td>
                <td style="text-align:center;">
                  <button @click.stop="removePoint(point.id)" class="btn-remove">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="16" height="16"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">Click map or upload file</div>

        <div class="control-group">
          <label>Buffer Radius (m):</label>
          <input 
            type="number" 
            v-model.number.lazy="bufferSize" 
            min="0" 
            step="100"
            @keyup.enter="$event.target.blur()"
          >
        </div>

        <div class="control-group" v-if="selectedPoints.length > 0">
		  <label>Export Data:</label>
		  <div class="export-buttons">
			
			<button 
			  @click="handleDownload" 
			  class="btn-download" 
			  :disabled="isDownloading"
			  style="margin-bottom: 10px;"
			>
			  <i class="fas" :class="isDownloading ? 'fa-spinner fa-spin' : 'fa-file-csv'"></i> 
			  {{ isDownloading ? 'Zipping...' : downloadLabel }}
			</button>

			<div class="button-row">
			  <button 
				@click="downloadChartImage" 
				class="btn-download half-width"
				:disabled="isDownloadingChart"
			  >
				<i class="fas" :class="isDownloadingChart ? 'fa-spinner fa-spin' : 'fa-chart-line'"></i>
				{{ isDownloadingChart ? 'Processing...' : chartDownloadLabel }}
			  </button>
			  
			  <button 
				@click="downloadMapAndGraph" 
				class="btn-download half-width"
				:disabled="isDownloadingMap"
			  >
				<i class="fas" :class="isDownloadingMap ? 'fa-spinner fa-spin' : 'fa-map'"></i>
				{{ isDownloadingMap ? 'Processing...' : mapDownloadLabel }}
			  </button>
			</div>
			
		  </div>
		</div>

        <p class="status-text">{{ statusMessage }}</p>
      </div>
    </div>
	
	<div class="resize-handle" @mousedown.prevent="startDrag">
       <div class="handle-grip"></div>
    </div>

    <div class="chart-wrapper" :style="{ height: (100 - mapHeightPercent) + '%' }">
		<div class="chart-controls-overlay" v-if="selectedPoints.length > 0 && plotOptions.length > 1">
			<span class="overlay-label">Graph View:</span>
			<select v-model="currentPlotVar" @change="updateChart" class="overlay-select">
			   <option v-for="opt in plotOptions" :key="opt.val" :value="opt.val">
				   {{ opt.label }}
			   </option>
			</select>
		  </div>
      <div id="velocity-chart" class="chart-container"></div>
    </div>
	
  </div>
  
  <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
      <div class="modal-content">
        <button class="modal-close" @click="showHelp = false">&times;</button>
        
        <h2>How to use SHIVER</h2>
        
        <div class="modal-body">
          <h3>1. Selecting Data</h3>
          <p>
            Click anywhere on the map or upload a shapefile containing a point or points to view 
			time-series of ice velocity in those locations. You can select up to ten points to compare different locations.
          </p>
		  <p>
            <strong>Explore timeseries chart:</strong> click-and-drag in the chart area to zoom in on a particular section of the chart. 
			Double click on the chart to reset the axes. Or use the zoom, pan and reset buttons in the top right of the chart to navigate.
          </p>
		  
		  <h3>2. About the data</h3>
          <p>
            This interactive map lets you extract and visualise time-series of ice velocity in West Greenland and the Antarctic Peninsula.
			The velocity estimates are generated by applying feature tracking techniques to pairs images acquired by the European Space Agency's
			Sentinel-1 satellite constellation. 
		  </p>
		  <p>
			With Sentinel-1,  the two images forming an image pair are always acquired a multiple of 6 days apart.
			We only use image pairs with a 6- or 12-day time separation, so all of the ice velocity measurements represent the average ice velocity over
			that 6- or 12-day period. The maps of ice velocity are posted to a 200 x 200 m grid, which is the approximate resolution of the measurements.
		  </p>
		  <p>
			Our processing system automatically generates new measurements of ice velocity every day, as Sentinel-1 acquires new images of the Earth.
			However, it can take a week or two for the new measurements to appear here.
		  </p>
		  <p>
			We provide the data at two quality levels: 'raw' and 'filt'. For both quality levels, we have attempted to remove erroneous velocity measurements 
			whilst preserving estimates that do represent the true ice surface velocity. The 'raw' data has had fewer outliers removed, whilst the 'filt' data
			has a more stringent outlier removal protocol:
		  </p>
		  <ul>
            <li><strong>raw:</strong> Although this is labelled 'raw', this data has had outliers removed using information only from spatial variations in estimated ice motion at each epoch.</li>
            <li><strong>filt:</strong>  In addition to the spatial filtering applied to the 'raw' data, the 'filt' data has additional outliers removed based on variations in ice speed and flow direction over time.</li>
          </ul>
		  <p>
			Low-latency access to these data is enabled using cloud-optimized zarr stores. 
		  </p>
		  <p>
			Read our <AppLink to="/documentation" class="text-link"><strong>documentation</strong></AppLink> page for more details.
          </p>
		  
          <h3>3. Uploading Shapefiles</h3>
          <p>
            <strong>Requirements:</strong>
          </p>
          <ul>
            <li><strong>Format:</strong> Zipped Shapefile (<code>.zip</code>) containing .shp, .shx, .dbf, and .prj files.</li>
            <li><strong>Projection:</strong> Must be in WGS84 (EPSG:4326) .</li>
            <li><strong>Type:</strong> Point or Multipoint geometries only. Maximum of ten points.</li>
          </ul>
		  <p>
            <strong>Optional:</strong>
          </p>
          <ul>
            <li><strong>Buffer:</strong> Include 'buffer' as a shapefile field name, containing integer buffer values for each point.</li>
            <li><strong>Point names:</strong> Include 'name' as a shapefile field name to give your outputs a custom name.</li>
          </ul>
		  
		  <h3>4. Advanced Options</h3>
          <p>
		     The advanced options allow you to select which ice velocity variable(s) and processing level(s) to extract, and allow you to tune the
			 timeseries smoothing parameters. 
		   </p>
		   <p>
            <strong>Variables:</strong>
          </p>
          <ul>
            <li><strong>S:</strong> Extract speed (horizontal ice surface velocity magnitude).</li>
            <li><strong>U:</strong> Extract easting velocity (horizontal ice surface easting velocity). Values are positive towards polar stereographic east.</li>
            <li><strong>V:</strong> Extract northing velocity (horizontal ice surface northing velocity). Values are positive towards polar stereographic north.</li>
          </ul>
		  <p>
            <strong>Processing level:</strong>
			See the <AppLink to="/documentation#mosaics" class="text-link">Mosaics section of our Documentation page</AppLink> for more details.
          </p>
          <ul>
            <li><strong>raw:</strong> Extract velocity from our 'raw' date-pair velocity mosaics.</li>
            <li><strong>filt:</strong> Extract velocity from our 'time filtered' date-pair velocity mosaics.</li>
          </ul>
		  <p>
            <strong>Smoothing parameters:</strong>
			All time-series extracted with SHIVER are smoothed using a Savitzky-Golay filter.
			Use the slide bars or text boxes to modify how much smoothing is applied.
          </p>
          <ul>
            <li><strong>Max gap fill length days:</strong> Small gaps in the point data are filled using linear interpolation. Use this option to control the maximum length of gap that is filled.</li>
            <li><strong>Window size days (Points):</strong> Set the size of the moving window used to smooth the point data displayed on the time-series chart. A larger window increases smoothing.</li>
			<li><strong>Window size days (Line):</strong> Set the size of the moving window used to smooth the line data displayed on the time-series chart. A larger window increases smoothing.</li>
			<li><strong>Polynomial order:</strong> Set the degree of the local polynomial fitted to the data within each moving window. A lower order increases smoothing but may distort rapid changes; a higher order better preserved high-frequences features but reduces smoothing.</li>
          </ul>
		  <p>
		    Note that the same variables and filtering level, using the same smoothing parameters, will be applied to all extraction locations.
		  </p>

          <h3>5. Interpreting the Map</h3>
          <p>
            Use the layer controls in the top-left to toggle between <strong>Velocity</strong>, 
            <strong>Measurement Count</strong>, and <strong>Speed Trend</strong>.
		  </p>
		  <ul>
            <li><strong>Speed:</strong> The average ice speed between October 2014 and November 2025, in metres per year.</li>
            <li><strong>Measurement count:</strong> The number of valid speed measurements available in each location, espressed as a percentage of the total number of measurements attempted in each location.</li>
			<li><strong>Speed Trend:</strong> The linear trend in speed from October 2014 through November 2025, in metres per year per year.</li>
			<li><strong>Ice Margin:</strong> This uses simplified versions of the PROMICE 2022 ice mask (Luetzenburg et al., 2025) for Greenland, 
			the ADD SCAR medium resolution Antarctic coastline (Gerrish et al., 2025) and the grounding line of Wallis et al. (2024)</li>
			<p>
			Luetzenburg, Gregor; Korsgaard, Niels J.; Deichmann, Anna K.; Socher, Tobias; Gleie, Karin; Scharffenberger, Thomas; Fahrner, Dominik; Nielsen, Eva B.; How, Penelope; Bjork, Anders A.; Kjeldsen, Kristian K.; Ahlstrom, Andreas P.; Fausto, Robert S., 2025, "PROMICE-2022 Ice Mask", https://doi.org/10.22008/FK2/O8CLRE, GEUS Dataverse, V3.
			</p>
			<p>
			Gerrish, L., Ireland, L., Fretwell, P., Cooper, P., & Skachkova, A. (2025). Medium resolution vector polylines of the Antarctic coastline (Version 7.11) [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/333065a9-633d-4005-ae41-fb7ae5ae7a91.
			</P>
			<p>
			Wallis, B.J., Hogg, A.E., Zhu, Y. and Hooper, A., 2024. Change in grounding line location on the Antarctic Peninsula measured using a tidal motion offset correlation method. The Cryosphere, 18(10), pp.4723-4742. https://doi.org/10.5194/tc-18-4723-2024.
			</p>
          </ul>
		  <p>
		    When viewing Antarctica, the outlines of glacier basins are shown as grey lines (Cook et al. 2014). If you zoom in sufficiently, glacier names from the
			<AppLink to="https://apc.antarctica.ac.uk/gazetteers/go-to-gazetteers/" target="_blank" rel="noopener" class="text-link">British Antarctic Territory gazetteer</AppLink> 
			will be displayed. 
		   </p>
		   <p>
		   Cook AJ, Vaughan DG, Luckman AJ, Murray T. A new Antarctic Peninsula glacier basin inventory and observed area changes since the 1940s. Antarctic Science. 2014;26(6):614-624. doi:10.1017/S0954102014000200
		   </p>
		     
		  
		  <h3>6. Output</h3>
		  <p>
		    Clicking the map will produce a timeseries showing point data and a smoothed line. 
			The point data provide the measurements taken directly from our ice velocity dataset.
			The line provides a smoothed representation of those measurements.
		  </p>
          <p>
            Download your timeseries as <strong>.csv</strong> files and/or the graph(s) as a , 
            <strong>.png</strong> file. If multiple points are selected, the extracted timeseries will be 
			downloaded as a .zip file containing multiple .csv files. If multiple variables 
			or filtering levels are selected, images will be downloaded as a .zip file.
			Downloads will also include a geojson of your point locations.
		  </p>
		  <p>
            <strong>CSV naming convention:</strong> <br>
			SiteName_Buffer_Lat_Lon_SmoothingParams.csv <br>
			e.g., Site_1_500m_67.123_-48.567_gf24_wr25_wd25_p2.csv <br>
			where: gf24 means gap_fill=24 days, wr25 means raw window smoothing length of 25 days, wd25 means a daily window smoothing length of 25 days, and p2 means a second order polynomial in the savitzky-golay smoother was used.
		  </p>
		  <p>
            <strong>CSV output variables:</strong>
			<br>
			<em>Note: Only "Date", "Error_m_yr", "Time_separation_days", "Pixel_Count" and "s_filt" are exported by default. 
			Other variables can be enabled for download within the Advanced Options menu. </em>
		  </p>
          <ul>
            <li><strong>Date:</strong> The central date of the two images used to estimate ice speed</li>
            <li><strong>Error_m_yr:</strong> An estimate of the global uncertainty in ice speed or velocity at this time period. Defined as the median speed over bedrock regions at that time.</li>
			<li><strong>Time_separation_days:</strong> The number of days between the two images used to estimate ice speed. So the first image was acquired on Date-Time_separation_days/2, and the second image on Date+Time_separation_days/2.</li>
			<li><strong>Pixel_Count:</strong> The number of valid speed estimates in the extraction location. This will be 1 if buffer=0. Pixel resolution is 200 metres, so the maximum value for e.g. a 500 m buffer is 25 (1000 x 1000 metre region = 5 x 5 pixel region).</li>
			<li><strong>s_filt:</strong> Horizontal ice surface speed in metres per year, from the time-filtered zarr store variable. If a buffer is used, the median speed within the resulted area is used.</li>
			<li><strong>s_raw:</strong> Horizontal ice surface speed in metres per year, from the raw (no time filtering) zarr store variable. If a buffer is used, the median speed within the resulted area is used.</li>
			<li><strong>u_filt:</strong> Horizontal  ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the time-filtered zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
			<li><strong>u_raw:</strong> Horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the raw (no time filtering) zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
			<li><strong>v_filt:</strong> Horizontal  ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the time-filtered zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
			<li><strong>v_raw:</strong> Horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the raw (no time filtering) zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
          </ul>
        </div>
      </div>
    </div>
	
</template>

<script setup>
// --- IMPORTS ---
import { ref, computed, nextTick, watch } from 'vue';
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LCircleMarker, LGeoJson, LControlLayers, LLayerGroup, LControlScale } from "@vue-leaflet/vue-leaflet";
import axios from 'axios';
import Plotly from 'plotly.js-dist-min'; 
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import L from 'leaflet';
import html2canvas from 'html2canvas';
import domtoimage from 'dom-to-image-more';

// --- API CONFIGURATION ---
// 1. Get the URL (Localhost in dev, Ngrok in prod)
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// 2. Create a custom Axios instance
// This automatically adds the base URL and the Ngrok bypass header to all requests
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'ngrok-skip-browser-warning': 'true',  // <--- The key to fixing the 404/Block page
    'Content-Type': 'application/json'
  }
});

// --- NATIVE GOOGLE ANALYTICS TRACKING ---
const trackEvent = (eventName, params = {}) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', eventName, params);
    console.log(`?? GA Event Sent: ${eventName}`, params);
  } else {
    console.log(`?? GA Event Skipped (Not loaded): ${eventName}`);
  }
};

// --- CONSTANTS ---
// Colors for selected points (cycles through this list)
const COLORS = [
  'rgb(1, 25, 89)', 'rgb(14, 55, 94)', 'rgb(28, 85, 97)', 
  'rgb(62, 108, 85)', 'rgb(105, 123, 62)', 'rgb(154, 136, 46)', 
  'rgb(213, 148, 72)', 'rgb(249, 163, 129)', 'rgb(253, 183, 189)', 'rgb(250, 204, 250)'
];

// Helper to create transparent versions of the colors for fill/error bars
const makePale = (rgb) => rgb.replace('rgb', 'rgba').replace(')', ', 0.3)');

// --- REACTIVE STATE ---
const map = ref(null);
const currentRegion = ref('Greenland');
const overlayLayer = ref('none'); // Tracks which visual layer is active (speed/count/trend)
const zoom = ref(8);
const center = ref([67.133129, -48.900752]);
const bufferSize = ref(500); 
const statusMessage = ref("");
const isDownloading = ref(false);
const isDownloadingChart = ref(false);
const isDownloadingMap = ref(false);
const isUploading = ref(false);
const selectedPoints = ref([]); 
const glacierData = ref(null);
const glacierNamesData = ref(null);
const showHelp = ref(false); 
const iceEdgeData = ref(null);
const groundingLineData = ref(null);
const showMargins = ref(false);
const mapHeightPercent = ref(60); // Default to 60%
const isDragging = ref(false);
const isFlowActive = ref(false);

// --- ADVANCED OPTIONS ---
const showAdvanced = ref(false);
const availableVars = ['s', 'u', 'v'];
const availableQuality = ['filt', 'raw'];
const selectedVars = ref(['s']);         
const selectedQuality = ref(['filt']);   
const currentPlotVar = ref('s_filt');    

// Smoothing Parameters
const smoothingParams = ref({
    gap: 24,
    win_raw: 1,
    win_daily: 25,
    poly: 2
});

const restoreDefaults = () => {
  selectedVars.value = ['s'];
  selectedQuality.value = ['filt'];
  smoothingParams.value = {
    gap: 24,
    win_raw: 1,
    win_daily: 25,
    poly: 2
  };
};

// --- Drag Logic ---
const startDrag = () => {
  isDragging.value = true;
  // Attach listeners to window so dragging continues even if mouse leaves the handle
  window.addEventListener('mousemove', onDrag);
  window.addEventListener('mouseup', stopDrag);
};

const onDrag = (e) => {
  if (!isDragging.value) return;

  const container = document.querySelector('.page-container');
  if (!container) return;

  // Calculate mouse Y position relative to the container top
  const containerRect = container.getBoundingClientRect();
  const relativeY = e.clientY - containerRect.top;
  
  // Convert to percentage
  let newHeight = (relativeY / containerRect.height) * 100;

  // Clamp limits (e.g., Map can't be smaller than 10% or larger than 90%)
  newHeight = Math.min(Math.max(newHeight, 10), 90);

  mapHeightPercent.value = newHeight;

  // CRITICAL: Tell Leaflet and Plotly the window size changed so they redraw
  window.dispatchEvent(new Event('resize'));
};

const stopDrag = () => {
  isDragging.value = false;
  window.removeEventListener('mousemove', onDrag);
  window.removeEventListener('mouseup', stopDrag);
  
  // Final resize trigger to ensure crisp rendering
  setTimeout(() => window.dispatchEvent(new Event('resize')), 100);
};

// Determine colour based on number of points
const distributeColors = () => {
  const n = selectedPoints.value.length;
  if (n === 0) return;

  // Map to a NEW array to ensure Vue detects the change deeply
  selectedPoints.value = selectedPoints.value.map((point, index) => {
    let newColor;
    if (n === 1) {
      newColor = COLORS[0];
    } else {
      const maxIndex = COLORS.length - 1;
      const colorIndex = Math.round(index * (maxIndex / (n - 1)));
      newColor = COLORS[colorIndex];
    }
    // Return a copy of the point with the new color
    return { ...point, color: newColor };
  });
};

// Add a timer variable outside the watch
let colorDebounceTimer;
// Watch to keep things in sync
watch(() => selectedPoints.value.length, () => {
  // 1. Immediate Update (Keeps it responsive)
  distributeColors();
  if (typeof updateChart === 'function') updateChart();

  // 2. "Cleanup" Update (The Fix)
  // This waits 200ms after the last change and forces one final color check.
  // This often fixes the "stuck on the last color" bug.
  clearTimeout(colorDebounceTimer);
  colorDebounceTimer = setTimeout(() => {
    distributeColors(); 
  }, 200);
});

// Generate suffix string for filenames: e.g. _gf24_wr25_wd25_p2
const smoothingSuffix = computed(() => {
    const p = smoothingParams.value;
    return `_gf${p.gap}_wr${p.win_raw}_wd${p.win_daily}_p${p.poly}`;
});

// Computed list of available plots based on selection
const plotOptions = computed(() => {
    const opts = [];
    selectedVars.value.forEach(v => {
        selectedQuality.value.forEach(q => {
            const labelMap = { s: 'Speed', u: 'Velocity U', v: 'Velocity V' };
            const typeMap = { filt: '(Filtered)', raw: '(Raw)' };
            opts.push({ val: `${v}_${q}`, label: `${labelMap[v]} ${typeMap[q]}` });
        });
    });
    return opts;
});

// Ensure currentPlotVar is valid; if not, reset
watch(plotOptions, (newOpts) => {
    if (newOpts.length > 0 && !newOpts.find(o => o.val === currentPlotVar.value)) {
        currentPlotVar.value = newOpts[0].val;
        updateChart();
    }
}, { deep: true });

// Dynamic label for the download button
const downloadLabel = computed(() => selectedPoints.value.length > 1 ? 'All CSVs (.zip)' : 'CSV');
const chartDownloadLabel = computed(() => plotOptions.value.length > 1 ? 'All Graphs (.zip)' : 'Graph' );
const mapDownloadLabel = computed(() => plotOptions.value.length > 1 ? 'All Maps (.zip)' : 'Map & Graph' );

// --- COMPUTED URLs FOR TILES ---
// "timestamp" is used as a query parameter (?t=...) to force the browser 
// to re-fetch tiles if the data changes, avoiding stale cache issues.
const timestamp = computed(() => Date.now()); 

// Note: Leaflet <img/> tags don't use axios, so we must construct the full URL string manually.
// We remove any trailing slash from API_URL to avoid double slashes like '...8000//api...'
const baseUrl = API_URL.replace(/\/$/, '');
const speedUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/speed/{z}/{x}/{y}.png?t=${timestamp.value}`);
const countUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/count/{z}/{x}/{y}.png?t=${timestamp.value}`);
const trendUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/trend/{z}/{x}/{y}.png?t=${timestamp.value}`);
const vectorUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/vectors/{z}/{x}/{y}.png?t=${timestamp.value}` );

// --- LEGEND & LAYER LOGIC ---
// Leaflet's <l-control-layers> handles the actual map toggling.
// These events listen to Leaflet to update our local 'overlayLayer' state,
// which determines which Legend bar to show in the bottom right.
const iceEdgeStyle = { color: "black", weight: 2 };
const groundingLineStyle = { color: "magenta", weight: 2 };

const onOverlayAdd = (e) => {  
  const rasterLayers = ['Ice Speed', 'Measurement Count', 'Speed Trend', 'Flow direction arrows'];
  if (rasterLayers.includes(e.name)) {
    // If clicking a raster layer, switch the active raster
	if (e.name === 'Ice Speed') overlayLayer.value = 'speed';
    if (e.name === 'Measurement Count') overlayLayer.value = 'count';
    if (e.name === 'Speed Trend') overlayLayer.value = 'trend';
	if (e.name === 'Flow direction arrows') isFlowActive.value = true;
  } 
  
  // Handle Ice Margin Selection
  if (e.name === 'Ice Margin') {
    showMargins.value = true;
    // Fetch data if we haven't already
    if (!iceEdgeData.value) loadMarginData();
  }
};

const onOverlayRemove = (e) => {
  // Only set to 'none' if the removed layer was the currently active one
  if (e.name === "Ice Speed" && overlayLayer.value === 'speed') overlayLayer.value = 'none';
  if (e.name === "Measurement Count" && overlayLayer.value === 'count') overlayLayer.value = 'none';
  if (e.name === "Speed Trend" && overlayLayer.value === 'trend') overlayLayer.value = 'none'; 
  if (e.name === "Flow direction arrows") isFlowActive.value = false; 
  
  // Margin data
  if (e.name === "Ice Margin") {
    showMargins.value = false;
  }
};

// FETCH MARGIN DATA ---
const loadMarginData = async () => {
  statusMessage.value = "Loading margin data...";
  try {
    // Load both files in parallel
    const [edgeRes, groundRes] = await Promise.all([
      apiClient.get('/static/iceedge_merged_simple.geojson'),
      apiClient.get('/static/apgroundingline_simple.geojson')
    ]);
    
    iceEdgeData.value = edgeRes.data;
    groundingLineData.value = groundRes.data;
    statusMessage.value = "Margin data loaded.";
  } catch (e) {
    console.error(e);
    statusMessage.value = "Error loading margins.";
  }
};

// Max speed label changes between Greenland (400) and Antarctica (800)
const maxSpeedLabel = computed(() => currentRegion.value === 'Greenland' ? '400 m/yr' : '800 m/yr');
const maxTrendLabel = computed(() => currentRegion.value === 'Greenland' ? '2.5' : '15');
const minTrendLabel = computed(() => currentRegion.value === 'Greenland' ? '-2.5' : '-15');
const vectorScaleLabel = computed(() => currentRegion.value === 'Greenland' ? '250 m/yr' : '500 m/yr');

// --- REFERENCE VECTOR CALCULATION --- //
const arrowPixelWidth = computed(() => {
  // Standard web map tiles are 256x256 pixels
  const tileSize = 256; 
  
  // Define the variables relative to the region
  let refSpeed;
  let backendScale;

  if (currentRegion.value === 'Greenland') {
     refSpeed = 250;       // User desired reference
     backendScale = 2250;  // Backend scale for Greenland
  } else {
     refSpeed = 500;       // User desired reference
     backendScale = 5000;  // Backend scale for Antarctica
  }

  // Calculate: (Reference / BackendScale) * 256px
  return (refSpeed / backendScale) * tileSize;
});


// --- REGION MANAGEMENT ---
const switchRegion = () => {
  clearAll(); // Remove points when switching context
  
  if (currentRegion.value === 'Greenland') {
    center.value = [67.133129, -48.900752]; zoom.value = 8;
  } else {
    center.value = [-66.323903, -63.355695]; zoom.value = 6;
  }
  
  // Force Leaflet to fly to the new center
  if (map.value && map.value.leafletObject) map.value.leafletObject.setView(center.value, zoom.value);
};

// --- DATA FETCHING & BUFFER LOGIC ---
let debounceTimer = null;
const debouncedRefetch = () => {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => { refetchAllPoints(); }, 600);
};

// Also watch smoothingParams deeply for changes
watch(smoothingParams, () => {
    debouncedRefetch();
}, { deep: true });

// Also watch for changes to buffer size
watch(bufferSize, (newValue) => {
  if (newValue === "" || newValue === null || newValue === undefined) {
    bufferSize.value = 500; return;
  }
  debouncedRefetch();
});


// Refetch data for ALL points with the new buffer size and/or new filtering option
const refetchAllPoints = async () => {
  if (selectedPoints.value.length === 0) return;
  
  const reqVars = selectedVars.value.length > 0 ? selectedVars.value : ['s'];
  const reqQual = selectedQuality.value.length > 0 ? selectedQuality.value : ['filt'];

  statusMessage.value = `Refreshing...`;
  try {
    const rois = selectedPoints.value.map(p => [p.lat, p.lon]);
    
    // Construct payload with all params
    const payload = {
      roi: rois, 
      buffer: bufferSize.value,
      variables: reqVars, 
      quality: reqQual,
      // Spread the smoothing params
      gap_fill: smoothingParams.value.gap,
      win_raw: smoothingParams.value.win_raw,
      win_daily: smoothingParams.value.win_daily,
      poly: smoothingParams.value.poly
    };

    const response = await apiClient.post('/api/timeseries/json', payload);
    const resultsArray = Object.values(response.data);
    resultsArray.forEach((newData, index) => {
      if (selectedPoints.value[index]) selectedPoints.value[index].data = newData;
    });
    updateChart(); 
    statusMessage.value = "Data updated.";
  } catch (error) {
    console.error("Failed to update:", error); statusMessage.value = "Error updating data.";
  }
};

// --- MAP INTERACTION ---
const onMapClick = async (e) => {
// 1. Validation Checks 
  const target = e.originalEvent?.target;
  if (!target || !target.isConnected) return;
  if (target.closest('.leaflet-control-container') || target.closest('.leaflet-control')) return;
  if (!map.value) return;
  
  if (selectedPoints.value.length >= 10) {
    alert("Maximum of 10 points allowed.");
    return;
  }
  
  // 2. Track clicks
  trackEvent("map_click", {
	  event_category: "interaction",
	  event_label: "extract_timeseries",
	  region: currentRegion.value,
	  lat: e.latlng.lat.toFixed(4),
	  lon: e.latlng.lng.toFixed(4)
	});
	
   const newId = `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
  //const color = COLORS[selectedPoints.value.length % COLORS.length];
  //await fetchSinglePoint(newId, e.latlng.lat, e.latlng.lng, color);
  await fetchSinglePoint(newId, e.latlng.lat, e.latlng.lng, COLORS[0]);
};

// Whenever points are added or removed, fix colors and update chart automatically.
watch(() => selectedPoints.value.length, () => {
  distributeColors();
  if (typeof updateChart === 'function') {
    updateChart();
  }
});


// Load static GeoJSON for glacier outlines (only if needed)
const loadGlacierOutlines = async () => {
  if (glacierData.value) return; 
  
  try {
    const response = await apiClient.get('/static/apbasinoutlines.geojson');
    glacierData.value = response.data;
  } catch (e) {
    console.error(e);
    statusMessage.value = "Failed to load outlines.";
  }
};

// Load glacier name labels
const loadGlacierNames = async () => {
  // Prevent double-fetching if already loaded
  if (glacierNamesData.value) return; 
  
  try {
    const response = await apiClient.get('/static/apc_glaciers_wkt.geojson');
    glacierNamesData.value = response.data;
  } catch (e) {
    console.error("Failed to load glacier names:", e);
    statusMessage.value = "Failed to load glacier names.";
  }
};

const glacierLabelOptions = {
  // Render invisible circle markers so we don't see blue pins
  pointToLayer: (feature, latlng) => {
    return L.circleMarker(latlng, {
      radius: 0,
      opacity: 0,
      fillOpacity: 0
    });
  },
  // Bind the permanent tooltip using the 'feature' property from your new file
  onEachFeature: (feature, layer) => {
    if (feature.properties && feature.properties.feature) {
      layer.bindTooltip(feature.properties.feature, {
        permanent: true,
        direction: 'center',
        className: 'glacier-label'
      });
    }
  }
};

// Auto-load outlines when switching to Antarctica
watch(currentRegion, (newVal) => {
  // --- GLACIER BASINS LOGIC ---
  // If moving to Antarctica, ensure basin data is loaded.
  // The check (!glacierData.value) ensures we don't fetch it twice.
  if (newVal === 'Antarctica' && !glacierData.value) {
    loadGlacierOutlines();
	loadGlacierNames();
  }
});

// Style for the glacier polygons (invisible fill, black outline #000000)
const outlineStyle = () => {
  return {
    color: "#708090",
    weight: 1,
    fillOpacity: 0  
  };
};



// --- FILE UPLOAD ---
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 1. Start loading state
  isUploading.value = true;
  statusMessage.value = "Uploading... 0%";
  
  const reqVars = selectedVars.value.length > 0 ? selectedVars.value : ['s'];
  const reqQual = selectedQuality.value.length > 0 ? selectedQuality.value : ['filt'];
  
  const formData = new FormData();
  formData.append("file", file);
  formData.append("buffer", bufferSize.value); 
  
  reqVars.forEach(v => formData.append("variables", v));
  reqQual.forEach(q => formData.append("quality", q));
  
  // Append smoothing params
  formData.append("gap_fill", smoothingParams.value.gap);
  formData.append("win_raw", smoothingParams.value.win_raw);
  formData.append("win_daily", smoothingParams.value.win_daily);
  formData.append("poly", smoothingParams.value.poly);

  try {
    const response = await apiClient.post('/api/timeseries/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
	  // Track upload progress
	  onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
		if (percentCompleted < 100) {
           statusMessage.value = `Uploading... ${percentCompleted}%`;
        } else {
           // Once we hit 100% upload, we are waiting for the server
           statusMessage.value = "Upload complete. Analyzing server response..."; }
        }
    });
	
    const results = response.data;
    if (results.status === 'error') throw new Error(results.message);
	
	// Convert to entries so we can iterate with index
    const entries = Object.entries(results);
	
	let added = 0;
    for (let i = 0; i < entries.length; i++) {
      if (selectedPoints.value.length >= 10) break;
      const [siteName, data] = entries[i];
      // Update status for the specific site
      statusMessage.value = `Processing site ${i + 1} of ${entries.length}...`;
      // Force a short (10ms) to let Vue render the text update.
      await new Promise(resolve => setTimeout(resolve, 2));
      // Parse data
      const ptLat = data.meta?.lat || 0;
      const ptLon = data.meta?.lon || 0;
      const color = COLORS[selectedPoints.value.length % COLORS.length];
      // Extract
      selectedPoints.value.push({
        id: Date.now() + added, lat: ptLat, lon: ptLon, color: color, data: data, name: siteName 
      });
      added++;
    }
	
    statusMessage.value = `Loaded ${added} sites.`;
    updateChart();
	
	// Clear input in case of additional uploads
	event.target.value = '';
	
  } catch (error) {
    console.error(error); statusMessage.value = "Upload failed.";
  } finally {
    isUploading.value = false;
  }
};

// Fetch data for a single point (used by Map Click)
const fetchSinglePoint = async (id, lat, lon, color) => {
  statusMessage.value = "Fetching...";
  const reqVars = selectedVars.value.length > 0 ? selectedVars.value : ['s'];
  const reqQual = selectedQuality.value.length > 0 ? selectedQuality.value : ['filt'];
  try {
    const payload = { 
        roi: [[lat, lon]], 
        buffer: bufferSize.value,
        variables: reqVars, 
        quality: reqQual,
        // Pass smoothing params
        gap_fill: smoothingParams.value.gap,
        win_raw: smoothingParams.value.win_raw,
        win_daily: smoothingParams.value.win_daily,
        poly: smoothingParams.value.poly
    };
    const response = await apiClient.post('/api/timeseries/json', payload);
    const rawData = response.data;
    const firstKey = Object.keys(rawData)[0];
    const siteData = rawData[firstKey];
    if (siteData.status === 'error') {
      statusMessage.value = `Error: ${siteData.message}`; return;
    }
    const newPoint = { id, lat, lon, color, data: siteData, name: firstKey };
    const idx = selectedPoints.value.findIndex(p => p.id === id);
    if (idx >= 0) selectedPoints.value[idx] = newPoint;
    else selectedPoints.value.push(newPoint);
    statusMessage.value = "Loaded.";
    updateChart();
  } catch (error) {
    console.error(error); statusMessage.value = "Server Error.";
  }
};

// Wrapper for updating a point when coords are manually edited
const refreshPointData = async (point) => await fetchSinglePoint(point.id, point.lat, point.lon, point.color);
const removePoint = (id) => { selectedPoints.value = selectedPoints.value.filter(p => p.id !== id); distributeColors(); updateChart(); };
const clearAll = () => { selectedPoints.value = []; Plotly.purge('velocity-chart'); };



// --- CHART PLOTTING (PLOTLY) ---
// BUILD CHART DATA (Returns {data, layout} for a given quality level)
const buildChartConfig = (plotKey) => {
  const traces = [];
  // plotKey example: "s_filt", "u_raw"
  
  selectedPoints.value.forEach((point, idx) => {
    if (point.data.status === 'error' || !point.data.data) return;
    
    // Data is now keyed directly: point.data.data['s_filt']
    const varData = point.data.data[plotKey];
    const rootData = point.data.data; // for shared x-axis, error, etc
    
    if (!varData) return;

    const pale = makePale(point.color);
    const label = /^Site_\d+$/.test(point.name) ? `P${idx+1}` : point.name;
    const suffix = plotKey.includes('raw') ? ' (Raw)' : '';

    traces.push({
      x: rootData.dates, y: varData.raw, mode: 'markers', type: 'scatter', 
      name: `${label}${suffix}`, legendgroup: `g${point.id}`, 
      marker: { color: pale, size: 5, line: {width:1, color: point.color} },
      error_y: { type: 'data', array: rootData.error, visible: true, color: pale, thickness: 1, width: 0 },
      error_x: { type: 'data', array: rootData.dt?.map(d=>d/2), visible: true, color: pale, thickness: 1, width: 0 }
    });
    
    traces.push({
      x: rootData.dates, y: varData.smoothed, mode: 'lines', type: 'scatter', 
      name: `${label}${suffix} Trend`, legendgroup: `g${point.id}`, 
      line: { color: point.color, width: 3 }
    });
  });
  
  // Determine y-axis label
  let yAxisLabel = "Velocity (m/yr)"; // Default fallback
  if (plotKey.startsWith('s')) {
    yAxisLabel = "Speed (m/yr)";
  } else if (plotKey.startsWith('u')) {
    yAxisLabel = "Easting velocity (m/yr, positive eastwards)";
  } else if (plotKey.startsWith('v')) {
    yAxisLabel = "Northing velocity (m/yr, positive northwards)";
  }

  const layout = {
    title: `Ice Velocity: ${plotKey.toUpperCase()}`,
    xaxis: { title: { text: 'Date', standoff: 15 }, showline: true, linewidth: 1, linecolor: 'black', mirror: true, automargin: true },
    yaxis: { title: { text: yAxisLabel, standoff: 15 }, showline: true, linewidth: 1, linecolor: 'black', mirror: true, automargin: true },
    margin: {t:40, r:20, l:80, b:60}, showlegend: true, legend: {orientation: 'h', y: 1.14, x: 0, xanchor: 'left'}, autosize: true
  };

  return { data: traces, layout };
};

// PLOT CHART
const updateChart = async () => {
  await nextTick(); 
  if (selectedPoints.value.length === 0) { Plotly.purge('velocity-chart'); return; }
  
  const { data, layout } = buildChartConfig(currentPlotVar.value);
  
  // Define the configuration
  const config = {
    responsive: true,
    // Add the specific button names you want to hide here
    modeBarButtonsToRemove: [
      'lasso2d',       // Lasso Select
      'select2d',      // Box Select
	  'toImage',       // Remove plotly image download (we replace with our own button that looks the same but performs better)
      'toggleSpikelines', // Toggle Spike Lines
	  'autoScale2D',   // Remove autoscale button (reset scale works just as well)
      'hoverClosestCartesian', // Often redundant if you use 'compare'
      'hoverCompareCartesian'  // Keep this if you want shared tooltips
    ],
	// 2. Add your custom button
    modeBarButtonsToAdd: [
      {
        name: 'custom_download', // Internal name
        title: 'Download Plot (PNG)', // Tooltip text
        icon: Plotly.Icons.camera,    // Use Plotly's default camera icon
        click: function(gd) {
          // 'gd' is the graph div, but downloadChartImage handles DOM retrieval itself.
          downloadChartImage();
        }
      }
    ],
    // Optional: Set to false if you want the bar hidden entirely until hover
    displayModeBar: 'hover', 
  };
  
  // Make the plot
  Plotly.newPlot('velocity-chart', data, layout, config);
};


// CHART IMAGE DOWNLOAD (MULTI-FILE SUPPORT) ---
const downloadChartImage = async () => {
  if (selectedPoints.value.length === 0) {
    statusMessage.value = "No chart to download.";
    return;
  }

  // --- Start Spinner ---
  isDownloadingChart.value = true;

  // Track png downloads (Left exactly as is)
  trackEvent("file_download", {
    event_category: "export",
    event_label: "png_chart",
    file_extension: "png",
    file_name: `velocity_plots_${currentRegion.value}`,
    plot_type: currentPlotVar.value
  });

  statusMessage.value = "Generating image(s)...";

  // --- Wrap in setTimeout to allow UI update ---
  setTimeout(async () => {
    try {
      const keysToDownload = plotOptions.value.map(o => o.val);

      if (keysToDownload.length === 1) {
        const graphDiv = document.getElementById('velocity-chart');
        // Append params suffix
        const fname = `velocity_${keysToDownload[0]}_timeseries${smoothingSuffix.value}`;
        await Plotly.downloadImage(graphDiv, {
          format: 'png', width: 1200, height: 500, filename: fname
        });
        statusMessage.value = "Image downloaded.";
        return;
      }

      // Existing Zip Logic (Left exactly as is)
      const zip = new JSZip();

      const getBlobForConfig = async (key) => {
        const tempDiv = document.createElement('div');
        tempDiv.style.width = '1200px'; tempDiv.style.height = '500px'; tempDiv.style.visibility = 'hidden';
        document.body.appendChild(tempDiv);
        const { data, layout } = buildChartConfig(key);
        await Plotly.newPlot(tempDiv, data, layout);
        const url = await Plotly.toImage(tempDiv, { format: 'png', width: 1200, height: 500 });
        document.body.removeChild(tempDiv);
        const res = await fetch(url);
        return await res.blob();
      };

      for (const k of keysToDownload) {
        const blob = await getBlobForConfig(k);
        // Append params suffix
        zip.file(`${currentRegion.value}_${k}_timeseries${smoothingSuffix.value}.png`, blob);
      }

      const content = await zip.generateAsync({ type: "blob" });
      saveAs(content, "velocity_plots.zip");
      statusMessage.value = "Images zipped.";
    } catch (e) {
      console.error(e);
      statusMessage.value = "Error saving images.";
    } finally {
      // --- Stop Spinner (Runs on success OR error) ---
      isDownloadingChart.value = false;
    }
  }, 50); // Short delay to let the browser paint the spinner
};


const downloadMapAndGraph = async () => {
  if (selectedPoints.value.length === 0) return;

  isDownloadingMap.value = true;
  statusMessage.value = "Preparing high-res images...";
  
  setTimeout(async () => {
    try {
      // --- 1. Capture the Map (Visuals Only) ---
      const mapElement = document.querySelector('.map-wrapper');
      
      // We use dom-to-image to capture the map EXACTLY as seen.
      // No manual drawing, no coordinate math.
      const mapImgUrl = await domtoimage.toPng(mapElement, {
          width: mapElement.clientWidth * 2,
          height: mapElement.clientHeight * 2,
          style: {
            transform: 'scale(2)',
            transformOrigin: 'top left', 
            width: `${mapElement.clientWidth}px`,
            height: `${mapElement.clientHeight}px`
          },
          // Filter out the controls (Zoom, etc.)
          filter: (node) => {
			// 1. Check if node has a classList (avoids errors on text nodes)
			if (node.classList) {
				// 2. Return FALSE to REMOVE these elements
				if (node.classList.contains('leaflet-control-container')) return false;
				if (node.classList.contains('control-panel')) return false;
				if (node.classList.contains('chart-controls-overlay')) return false;
			}
			// 3. Return TRUE to KEEP everything else
			return true;
		}
      });

      // Load Map Image
      const mapImg = new Image();
      mapImg.src = mapImgUrl;
      await new Promise(resolve => mapImg.onload = resolve);

      // --- 2. Zip & Loop (Standard Logic) ---
      const zip = new JSZip();
      const optionsProcess = plotOptions.value.length > 0 ? plotOptions.value : [{val: currentPlotVar.value}];
      const filesToSave = [];

      for (const opt of optionsProcess) {
        statusMessage.value = `Processing ${opt.label}...`;

        // Generate Chart
        const { data, layout } = buildChartConfig(opt.val);
        
        // High-Res Chart Layout
        const printLayout = { 
          ...layout, 
          title: { ...layout.title, font: { size: 24 } }, 
          xaxis: { ...layout.xaxis, title: { ...layout.xaxis.title, font: { size: 18 } } },
          yaxis: { ...layout.yaxis, title: { ...layout.yaxis.title, font: { size: 18 } } },
        };

        const chartImgUrl = await Plotly.toImage(
          { data, layout: printLayout }, 
          { format: 'png', width: 1400, height: 600, scale: 2 }
        );

        const chartImg = new Image();
        chartImg.src = chartImgUrl;
        await new Promise(resolve => chartImg.onload = resolve);

        // Merge Canvas
        const combinedCanvas = document.createElement('canvas');
        const ctx = combinedCanvas.getContext('2d');
        const finalWidth = Math.max(mapImg.width, chartImg.width);
        const finalHeight = mapImg.height + chartImg.height;

        combinedCanvas.width = finalWidth;
        combinedCanvas.height = finalHeight;

        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(0, 0, finalWidth, finalHeight);
        ctx.drawImage(mapImg, 0, 0);
        ctx.drawImage(chartImg, 0, mapImg.height);

        const blob = await new Promise(resolve => combinedCanvas.toBlob(resolve, 'image/png'));
        const fname = `velocity_${opt.val}_timeseries${smoothingSuffix.value}_map.png`;
        filesToSave.push({ name: fname, blob: blob });
      }

      // --- 3. Save ---
      if (filesToSave.length === 1) {
        saveAs(filesToSave[0].blob, filesToSave[0].name);
        statusMessage.value = "Image downloaded.";
      } else {
        filesToSave.forEach(f => zip.file(f.name, f.blob));
        statusMessage.value = "Compressing...";
        const content = await zip.generateAsync({type:"blob"});
        saveAs(content, `Map_Velocity_Export_${currentRegion.value}.zip`);
        statusMessage.value = "All charts downloaded.";
      }

    } catch (error) {
      console.error("Map Export Error:", error);
      statusMessage.value = "Error generating images.";
    } finally {
      isDownloadingMap.value = false;
    }
  }, 100);
};

// Helper: Generates filenames for download
const getFilename = (p, index) => {
  const meta = p.data.meta || {};
  let name = meta.site_name || p.name || 'Site';
  if (/^Site_\d+$/.test(name)) name = `Site_${index + 1}`;
  const buf = meta.buffer_used !== undefined ? meta.buffer_used : bufferSize.value;
  // Use toFixed(3) for lat/lon as requested previously + params
  const lat = p.lat.toFixed(3);
  const lon = p.lon.toFixed(3);
  return `${name}_${buf}m_${lat}_${lon}${smoothingSuffix.value}.csv`;
};

// --- DATA DOWNLOAD HANDLER ---
const handleDownload = async () => {
  if (selectedPoints.value.length === 0) return;
  
  // Track csv downloads
  trackEvent("file_download", {
	  event_category: "export",
	  event_label: "csv_data",
	  file_extension: "zip", // or csv
	  file_name: "velocity_data_batch",
	  region: currentRegion.value,
	  count: selectedPoints.value.length
	});
  
  // Single File: Direct CSV download
  if (selectedPoints.value.length === 1) {
    const p = selectedPoints.value[0];
    const blob = new Blob([generateCSV(p)], { type: "text/csv;charset=utf-8" });
    saveAs(blob, getFilename(p, 0)); 
    return;
  }

  // Multiple Files: Zip archive
  isDownloading.value = true;
  try {
    const zip = new JSZip();
    
    // 1. Add CSVs
    selectedPoints.value.forEach((p, index) => {
      zip.file(getFilename(p, index), generateCSV(p));
    });

    // 2. Add GeoJSON Summary
    const geojson = {
      type: "FeatureCollection",
      features: selectedPoints.value.map((p, index) => {
        let name = p.name || `Site_${p.id}`;
        if (/^Site_\d+$/.test(name)) name = `Site_${index + 1}`;

        return {
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: [p.lon, p.lat] 
          },
          properties: {
            id: index + 1,
            name: name,
            buffer_m: p.data.meta?.buffer_used || bufferSize.value,
            region: currentRegion.value
          }
        };
      })
    };

    zip.file("sites.geojson", JSON.stringify(geojson, null, 2));

    const content = await zip.generateAsync({ type: "blob" });
    saveAs(content, "velocity_data_batch.zip");
  } catch (e) {
    statusMessage.value = "Zip Error.";
    console.error(e);
  } finally {
    isDownloading.value = false;
  }
};

// CSV Generator
const generateCSV = (point) => {
  const rootData = point.data.data; 
  if (!rootData) return "";

  // Fixed Headers
  let csv = "Date,Error_m_yr,Time_Separation_days,Pixel_Count";
  
  // Find all available data keys (s_filt, u_raw, etc)
  const availableKeys = Object.keys(rootData).filter(k => !['dates','error','dt','count'].includes(k));
  
  availableKeys.forEach(k => {
      csv += `,${k}`; 
  });
  csv += "\n";

  // Iterate through dates
  rootData.dates.forEach((date, i) => {
	  // If NaN, skip it
	  if (availableKeys.length > 0) {
			const firstKey = availableKeys[0];
			const checkVal = rootData[firstKey].raw[i];
			// If the value is null, undefined, or NaN, skip this iteration
			if (checkVal === null || checkVal === undefined || Number.isNaN(checkVal)) { return; }
	}
	// Build row
    const error = rootData.error ? rootData.error[i] : '';
    const dt = rootData.dt ? rootData.dt[i] : '';
    const count = rootData.count ? rootData.count[i] : 0;
    
    let row = `${date},${error},${dt},${count}`;
    availableKeys.forEach(k => {
        const val = rootData[k].raw[i];
        row += `,${val !== null ? val : ''}`;
    });
    csv += row + "\n";
  });
  
  return csv;
};
</script>

<style scoped>
/* --- MAIN LAYOUT --- */
.page-container { display: flex; flex-direction: column; height: calc(100vh - 60px); width: 100%; overflow: hidden; }
.map-wrapper { position: relative; width: 100%; user-select: none; }
.chart-wrapper { width: 100%; background: white; position: relative; overflow: hidden;}
.chart-container { width: 100%; height: 100%; }
.chart-controls-overlay {
  position: absolute; top: 25px; right: 10px; z-index: 100;  display: flex; 
  align-items: center; gap: 8px; background-color: rgba(255, 255, 255, 0.9); 
  padding: 4px 8px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
  font-size: 0.85rem;
}
.overlay-select { padding: 2px 4px; border: 1px solid #ccc; border-radius: 4px; font-size: 0.85rem; background-color: white; }

.resize-handle {
  width: 100%;
  height: 2px; /* Hit area height */
  background-color: #f1f1f1;
  cursor: row-resize; /* The up/down arrow cursor */
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #ccc;
  border-bottom: 1px solid #ccc;
  flex-shrink: 0; /* Prevent the handle itself from squishing */
  z-index: 2000; /* Ensure it sits above map controls */
}

.resize-handle:hover { background-color: #e0e0e0; }

/* The little visual "grip" lines in the middle */
.handle-grip { width: 40px; height: 4px; border-top: 2px solid #999; border-bottom: 2px solid #999; }

/* --- CONTROL PANEL (RIGHT SIDEBAR) --- */
.control-panel {
  position: absolute; top: 10px; right: 10px; z-index: 1000;
  background: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2); width: 320px; max-height: 80%; overflow-y: auto; font-family: sans-serif;
}
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }

/* --- BRANDING (SHIVER) --- */
.brand-header {
  position: relative; /* Added: Establishes the boundary for absolute positioning */
  padding-bottom: 15px; margin-bottom: 15px;
  border-bottom: 2px solid #f0f0f0; text-align: center;
}

.shiver-title {
  margin: 0; font-size: 26px; font-weight: 700; color: #0056b3; line-height: 1; letter-spacing: 1px;
}
.shiver-subtitle {
  margin-top: 6px; font-size: 13px; font-weight: 600; color: #5a9bd4; letter-spacing: 0.5px;
}

/* --- HELP BUTTON (?) --- */
.btn-help, .btn-gear {
  /* Positioning */
  position: absolute;
  top: 0px;   /* Aligns to the top edge of brand-header padding */
  /* Styling (Subtle, smaller, grey/blue tone) */
  background: transparent;
  color: #aab8c2; /* Pale grey-blue */
  border: 2px solid #e1e8ed; /* Very subtle border definition */
  /* Sizing */
  width: 25px; height: 25px; font-size: 14px; font-weight: bold; 
  /* Standard button stuff */
  border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
/* Help is Right aligned */
.btn-help { right: 0px; }
/* Gear is Left aligned */
.btn-gear { left: 0px; font-size: 16px; padding: 3px; }

.btn-help:hover, .btn-gear:hover {
  background: #f5f8fa;
  color: #0056b3; /* Turns the brand color on hover */
  border-color: #0056b3;
}

/* --- ADVANCED OPTIONS POPUP --- */
.advanced-popup {
    background: #f9fbfd;
    border: 1px solid #0056b3;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.popup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 5px; color: #0056b3; }
.popup-close { border: none; background: none; font-size: 18px; cursor: pointer; color: #999; }
.popup-close:hover { color: red; }
.opt-section { margin-bottom: 8px; }
.opt-label { display: block; font-size: 0.85rem; font-weight: bold; color: #666; margin-bottom: 4px; }
.opt-checks { display: flex; flex-direction: row; flex-wrap: wrap; gap: 15px; align-items: center; }
.opt-checks label { display: flex; align-items: center; gap: 4px; font-size: 0.8rem; cursor: pointer; white-space: nowrap; }
.param-row { display: flex; align-items: center; justify-content: space-between; gap: 5px; font-size: 0.75rem; }
.param-row label { flex: 1; color: #555; }
.param-slider { flex: 1; height: 4px; }
.param-input { width: 40px; padding: 2px; text-align: right; border: 1px solid #ccc; border-radius: 3px; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px; /* Space between 'Restore defaults' and 'X' */
}

/* 3. Style the Restore button as a text link */
.btn-restore-link {
  background: transparent;
  border: none;
  color: #95a5a6; /* Subtle grey */
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0;
  transition: all 0.2s;
}

/* 4. Hover Effects: Red + Underline */
.btn-restore-link:hover {
  color: #c0392b;
  text-decoration: underline;
}

/* (Make sure .popup-close doesn't have huge margins that break alignment) */
.popup-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #666;
  cursor: pointer;
  padding: 0;
}
.popup-close:hover {
  color: #c0392b;
}

/* --- HELP MODAL OVERLAY --- */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center;
  z-index: 9999; backdrop-filter: blur(2px);
}
.modal-content {
  background: white; padding: 30px; width: 90%; max-width: 600px;
  border-radius: 12px; box-shadow: 0 15px 50px rgba(0,0,0,0.3);
  position: relative; max-height: 85vh; overflow-y: auto;
}
.modal-content h2 { margin-top: 0; color: #0056b3; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; margin-bottom: 20px; }
.modal-content h3 { font-size: 1.1rem; color: #333; margin-bottom: 8px; margin-top: 20px; }
.modal-content p, .modal-content li { color: #555; line-height: 1.6; font-size: 0.95rem; }
.modal-close { position: absolute; top: 15px; right: 20px; background: none; border: none; font-size: 28px; color: #999; cursor: pointer; }
.modal-close:hover { color: #333; }

/* --- PANEL COMPONENTS --- */
.panel-section { margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
.panel-section label { font-weight: bold; margin-right: 10px; color: #333; }
.panel-section select { padding: 5px; border-radius: 4px; border: 1px solid #ccc; width: 60%; }

.upload-section { margin-bottom: 15px; text-align: center; }
.btn-upload { display: inline-block; padding: 8px 12px; background: #6c757d; color: white; border-radius: 4px; cursor: pointer; font-size: 0.9rem; font-weight: bold; width: 100%; }

.list-toolbar { display: flex; justify-content: flex-end; margin-bottom: 5px; }
.btn-clear { background: none; border: none; color: #d9534f; cursor: pointer; font-size: 0.8rem; text-decoration: underline; padding: 0; }

.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  vertical-align: middle; /* Aligns spinner with text baseline if needed */
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-upload.is-loading {
  pointer-events: none;
  opacity: 0.8;
}

.page-container.is-global-loading,
.page-container.is-global-loading * {
  cursor: wait !important;
}

/* --- POINTS LIST --- */
.points-list table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-bottom: 15px; }
.points-list th { text-align: left; padding: 4px; color: #555; }
.points-list td { padding: 4px; border-bottom: 1px solid #eee; }
.color-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; }
.coord-input { width: 70px; padding: 4px; font-size: 0.85rem; border: 1px solid #ddd; border-radius: 3px; }
.btn-remove { border: none; background: transparent; color: #999; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; padding: 4px; border-radius: 4px; transition: all 0.2s ease; }
.btn-remove:hover { color: #dc3545; background-color: rgba(220, 53, 69, 0.1); }

/* --- GENERAL CONTROLS --- */
.control-group { margin-bottom: 15px; }
.control-group label { display: block; font-size: 0.9rem; margin-bottom: 4px; font-weight: 600; }
.control-group input[type="number"] { width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px; }
.status-text { font-size: 0.8rem; color: #666; margin-top: 10px; text-align: center; min-height: 1.2em;}
.empty-state { padding: 15px; text-align: center; color: #888; border: 1px dashed #ccc; border-radius: 4px; margin-bottom: 15px; font-size: 0.9rem;}
.download-group { display: flex; justify-content: space-between; gap: 10px; margin-top: 15px; width: 100%; }
/* Layout Container for the buttons */
.export-buttons { width: 100%; display: flex; flex-direction: column; }

/* Row container for the two side-by-side buttons */
.button-row { display: flex; gap: 10px; width: 100%; }

/* Helper to make buttons share width equally */
.half-width { flex: 1; }

/* Your existing button style (Confirmed from previous turn) */
.btn-download { width: 100%; background-color: #2c3e50; color: white; 
  border: none;  padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; transition: background-color 0.2s;
  display: flex; align-items: center; justify-content: center; gap: 8px; }

.btn-download:hover:not(:disabled) { background-color: #42b983; }
.btn-download:disabled { background-color: #95a5a6; cursor: not-allowed; }

/* --- MAP LEGEND --- */
.map-legend {
  position: absolute; bottom: 30px; right: 340px; z-index: 999;
  background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2); width: 240px; font-family: sans-serif; pointer-events: none;
}
.map-legend h4 { margin: 0 0 10px 0; font-size: 0.85rem; color: #333; text-align: center; font-weight: 600; }
.legend-bar { height: 18px; width: 100%; border-radius: 2px; border: 1px solid #ccc; margin-bottom: 5px; }
.legend-labels { display: flex; justify-content: space-between; margin-top: 6px; font-size: 0.75rem; color: #444; font-weight: bold; }

.legend-container {
  position: absolute;
  bottom: 30px;
  left: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column; /* This ensures they stack */
  align-items: flex-start;
  gap: 10px; /* Space between the two legends */
  pointer-events: none; /* Allow clicks to pass through empty space */
  min-width: 120px;
}

.scalar-legend-group {
  margin-bottom: 5px;
}

.legend-separator {
  height: 1px;
  background-color: #ddd;
  margin: 8px 0;
  width: 100%;
}

/* Vector Section Layout */
.vector-legend-group {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.vector-row {
  display: flex;
  align-items: center;
  gap: 8px; /* Space between arrow tip and text */
  margin-top: 2px;
}

.vector-label {
  font-size: 0.75rem;
  color: #444;
  font-weight: 600;
  white-space: nowrap;
}

/* Ensure the SVG handles overflow correctly */
.vector-arrow-svg {
  display: block; /* Removes weird inline spacing */
  overflow: visible;
}

.legend-box {
  background: white;
  padding: 10px;
  border-radius: 4px;
  box-shadow: 0 0 10px rgba(0,0,0,0.2);
  width: 200px;
  pointer-events: auto; /* Re-enable clicks on the box itself */
  font-family: sans-serif;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-top: 8px;
  font-size: 0.8rem;
  color: #333;
}

.legend-line {
  width: 30px;
  height: 3px;
  margin-right: 10px;
  border-radius: 1px;
}

/* --- SCALE BAR --- */
:deep(.leaflet-control-scale-line) {
  /* 1. Semi-transparent white background */
  background: rgba(255, 255, 255, 0.7) !important;
  
  /* 2. Black Borders */
  border-color: black !important;
  border-width: 2px !important;
  
  /* 3. Text Styling */
  color: black !important;
  font-weight: bold;
  font-size: 12px;
  
  /* Optional: Adjust padding for a cleaner look */
  padding: 2px 5px 0 5px !important;
  
  /* Ensure the 'ticks' (side borders) are visible */
  border-top: none !important;
  line-height: 1.1;
}

/* --- GLACIER LABELS --- */
/* We target the class defined in the JS options above */
:deep(.glacier-label) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 10px; /* Small font to reduce clutter */
  font-weight: bold;
  color: #333;
  text-align: center;
  /* Add a white halo so text is readable on dark/complex backgrounds */
  text-shadow: 
    -1px -1px 0 #fff,  
     1px -1px 0 #fff,
    -1px  1px 0 #fff,
     1px  1px 0 #fff;
  
  /* Hide by default (opacity allows for smooth transition) */
  opacity: 0 !important;
  visibility: hidden;
  transition: opacity 0.3s ease;
  pointer-events: none; /* Let clicks pass through to the polygon/map */
}

/* Only show when the parent map-wrapper has the 'show-labels' class */
.show-labels :deep(.glacier-label) {
  opacity: 1 !important;
  visibility: visible;
}

/* HEADERS */
.legend-box h4 {
  margin: 0 0 8px 0;
  font-size: 0.9rem;
  color: #333;
  text-align: center;
}

/* BAR STYLING */
.legend-bar {
  height: 15px;
  width: 100%;
  border: 1px solid #ccc;
  margin-bottom: 5px;
}

.legend-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #666;
}

/* LEGEND GRADIENTS */
.viridis-gradient {
  background: linear-gradient(to right, #440154, #482878, #3e4989, #31688e, #26828e, #1f9e89, #35b779, #6ece58, #b5de2b, #fde725);
}
.trend-gradient {
  background: linear-gradient(to right, #0000FF 0%, #4040FF 12.5%, #8080FF 25%, #BFBFFF 37.5%, #FFFFFF 50%, #FFBFBF 62.5%, #FF8080 75%, #FF4040 87.5%, #FF0000 100%);
}
.speed-gradient {
  /* Complex gradient from previous step */
  background: linear-gradient(to right, 
    #FFFFFF 0.22%, #FFFFFF 14.9%, #FDFFFF 16.0%, #E4FFFE 20.5%, #D7FFFE 24.0%, #D7FFFE 45.4%,
    #D1FBFB 46.6%, #70BACE 50%, #308FB1 52.2%, #03719C 54.5%, #03719C 61.3%, #167798 62.4%, 
    #548B8A 64.7%, #939E7D 66.9%, #D1B26F 69.2%, #C75D0F 76.0%, #D42C01 80.5%, #E20000 85.0%, 
    #C50000 87.3%, #990000 90.7%, #6F0000 95.2%, #4C0100 99.7%
  );
}

</style>

<style>
/* LEAFLET OVERRIDES (Global Style)
   Force layer control to expand on hover instead of click 
*/
.leaflet-control-layers:hover {
  padding: 6px 10px 6px 6px !important;
  background: #fff !important;
  color: #333 !important;
  box-shadow: 0 1px 5px rgba(0,0,0,0.4) !important;
  border-radius: 5px !important;
}
.leaflet-control-layers:hover .leaflet-control-layers-list { display: block !important; }
.leaflet-control-layers:hover .leaflet-control-layers-toggle { display: none !important; }
</style>