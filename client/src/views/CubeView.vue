<template>
  <div class="page-container" :class="{ 'is-global-loading': isUploading  }">
    
    <div class="map-wrapper" :class="{ 'show-labels': zoom >= 9 }" :style="{ height: mapHeightPercent + '%' }">
      <l-map 
        ref="map" 
        v-model:zoom="zoom" 
        v-model:center="center" 
        :use-global-leaflet="true" 
		:options="{ zoomControl: false }"
		@ready="onMapReady"
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
		  crossOrigin="anonymous"
        ></l-tile-layer>
		
		<div class="map-title-overlay">
		  <h1 class="shiver-title">SHIVER</h1>
		  <div class="shiver-subtitle">Data Cube Extractor</div>
		</div>
		
		<transition name="fade">
		  <div 
			  v-if="showFeedbackPopup" 
			  class="feedback-popup"
			  @click.stop
			  @mousedown.stop
			  @dblclick.stop
		  >
          <div class="feedback-content">
             Enjoying SHIVER? Please complete 
             <a 
               href="YOUR_GOOGLE_FORM_LINK_HERE" 
               target="_blank" 
               class="feedback-link"
               @click="closeFeedbackPopup"
             >
               this short form
             </a> 
             to provide feedback.
          </div>
          
          <button class="feedback-close" @click="closeFeedbackPopup">
            &times;
          </button>
        </div>
      </transition>
	  
		<Transition name="fade">
			  <div v-if="statusMessage" class="status-toast">
				<div class="status-content">
				  <span class="message-display-spinner" v-if="isMessageSpinnerRequired"></span>
				  {{ statusMessage }}
				</div>
			  </div>
		</Transition>
		
		<l-tile-layer
          :url="hillshadeUrl"
          :opacity="1.0"
		  :z-index="10" 
          layer-type="overlay"
          name="Topography"
          :visible="false"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>

        <l-tile-layer
          :url="speedUrl"
          :opacity="0.5"
		  :z-index="30"
          layer-type="overlay"
          name="Ice Speed"
          :visible="overlayLayer === 'speed'"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>

        <l-tile-layer
          :url="countUrl"
          :opacity="0.5"
		  :z-index="30"
          layer-type="overlay"
          name="Measurement Count"
          :visible="overlayLayer === 'count'"
		  :options="{ crossOrigin: 'anonymous' }"
        ></l-tile-layer>
		
        <l-tile-layer
          :url="trendUrl"
          :opacity="0.5"
		  :z-index="30"
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
			:z-index="50" 
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
		
		<l-geo-json 
			  v-if="globalMaskData" 
			  :geojson="globalMaskData"
			  :options-style="() => ({ fillColor: '#ffffff', fillOpacity: 0.65, weight: 0, stroke: false })"
			  :options="{ interactive: false }"
	    ></l-geo-json>

		<l-geo-json 
			  v-if="globalOutlineData" 
			  :geojson="globalOutlineData"
			  :options-style="() => ({ color: 'black', weight: 2, fill: false, dashArray: '5, 5' })"
		></l-geo-json>
	   
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

        <div class="legend-box" v-if="overlayLayer !== 'none' || isFlowActive || showMargins">
        
			<div v-if="overlayLayer !== 'none'" class="scalar-legend-group">
				<div v-if="overlayLayer === 'speed'">
				  <h4>Ice Speed (Log Scale)</h4>
				  <div class="legend-bar speed-gradient"></div>
				  <div class="legend-bar-labels">
					<span>1</span>
					<span>10</span>
					<span>150</span>
					<span>{{ maxSpeedLabel }}</span>
				  </div>
				</div>

				<div v-else-if="overlayLayer === 'count'">
				  <h4>Percentage Valid Measurements</h4>
				  <div class="legend-bar viridis-gradient"></div>
				  <div class="legend-bar-labels">
					<span>0</span>
					<span>30</span>
					<span>60</span>
					<span>90</span>
				  </div>
				</div>
		
				<div v-else-if="overlayLayer === 'trend'">
				  <h4>Speed Trend (m/yr<sup>2</sup>)</h4>
				  <div class="legend-bar trend-gradient"></div>
				  <div class="legend-bar-labels">
					<span>{{ minTrendLabel }}</span>
					<span>0</span>
					<span>{{ maxTrendLabel }}</span>
				  </div>
				</div>
			</div>
			
			<div v-if="isFlowActive" class="vector-legend-group">
				<div v-if="overlayLayer !== 'none'" class="legend-separator"></div>				
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
					   :x2="Math.max(arrowPixelWidth, 20) + 5" y2="12"
					   stroke="#333" 
					   stroke-width="2" 
					   marker-end="url(#arrowhead)" 
					 />
				  </svg>
				  <span class="vector-label">{{ vectorScaleLabel }}</span>
				</div>
			</div>
			
			<div v-if="showMargins" style="margin-top: 2px; border-top: 1px solid #ccc; padding-top: 2px;">			  
			  <div class="map-legend-item">
				<div class="map-legend-line" style="background: black;"></div>
				<span class="map-legend-label">Ice Margin</span>
			  </div>

			  <div class="map-legend-item" v-if="currentRegion === 'Antarctica'">
				<div class="map-legend-line" style="background: magenta;"></div>
				<span class="map-legend-label">Grounding Line</span>
			  </div>
			</div>
			
		</div>
		
	  </div>
	  
      <div class="map-toolbar">
	  
		  <div class="menu-trigger">
			<button class="panel-btn" title="Open Toolbox">
			  <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none">
				<line x1="3" y1="12" x2="21" y2="12"></line>
				<line x1="3" y1="6" x2="21" y2="6"></line>
				<line x1="3" y1="18" x2="21" y2="18"></line>
			  </svg>
			</button>
		  </div>
		  
		  <div class="tools-wrapper">

			  <div class="toolbar-group">
				<button 
				  class="panel-btn" 
				  :class="{ 'active': currentRegion === 'Greenland' }"
				  @click="currentRegion = 'Greenland'; switchRegion()"
				  title="Switch to Greenland"
				>
				  <greenlandIcon class="btn-icon-svg" />
				</button>

				<button 
				  class="panel-btn" 
				  :class="{ 'active': currentRegion === 'Antarctica' }"
				  @click="currentRegion = 'Antarctica'; switchRegion()"
				  title="Switch to Antarctica"
				>
				  <antarcticaIcon class="btn-icon-svg" />
				</button>
			  </div>

			  <div class="toolbar-group">
				<label 
				  class="panel-btn" 
				  :class="{ 'active': isUploading }" 
				  title="Upload File (KML, KMZ, GeoJSON or zipped shapefile)"
				>
				  <input type="file" @change="handleFileUpload" accept=".zip,.geojson,.kml,.kmz" hidden :disabled="isUploading">
				  <span v-if="isUploading" class="spinner-small"></span>
				  <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="17 8 12 3 7 8" />
					<line x1="12" y1="3" x2="12" y2="15" />
				  </svg>
				</label>
				
				<button class="panel-btn" @click="showHelp = true" title="Help">
				  <span><strong>?</strong></span>
				</button>
			  </div>
			  
			</div>
			
		</div>
			
	</div>
	
	<div class="resize-handle" @mousedown.prevent="startDrag" @touchstart.prevent="startDrag">
       <div class="handle-grip"></div>
    </div>

	<div class="cube-controls" :style="{ height: (100 - mapHeightPercent) + '%' }">
    
		<div class="controls-header">
		  <div class="header-content">
			<h3><span class="icon">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
					<path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
				</svg>
			</span> Cube Configuration</h3>
			<p class="instruction">Draw a region on the map and select parameters.</p>
		  </div>
		</div>

		<div class="controls-body">
		  <div class="control-card">
			<label class="section-label">Time Period</label>
			<div class="date-row">
			  <div class="input-group">
				<span class="sub-label">Start</span>
				<input type="date" v-model="startDate" class="dark-input">
			  </div>
			  <div class="input-group">
				<span class="sub-label">End</span>
				<input type="date" v-model="endDate" class="dark-input">
			  </div>
			</div>
			
			<label class="section-label mt-3">Frequency</label>
			<div class="select-wrapper">
			  <select v-model="frequency" class="dark-input full-width">
				<option value="native">Native (Approx. Weekly)</option>
				<option value="monthly">Monthly Mean</option>
				<option value="quarterly">Quarterly Mean</option>
				<option value="annual">Annual Mean</option>
			  </select>
			</div>
		  </div>

		  <div class="control-card">
			<label class="section-label">Variables</label>
			<div class="checkbox-scroller">
			  <div class="checkbox-grid">
				<label 
				  v-for="v in availableVariables" 
				  :key="v.id" 
				  class="checkbox-item"
				  :class="{ 'checked': selectedVariables.includes(v.id) }"
				>
				  <input type="checkbox" :value="v.id" v-model="selectedVariables" hidden>
				  <span class="custom-check"></span>
				  <span class="var-name">{{ v.name }}</span>
				</label>
			  </div>
			</div>
		  </div>

		  <div class="control-card action-card">
			<div class="status-area">
			
				<div v-if="!isRegionDrawn" class="status-msg warning">
				   Upload file or draw a region on the map
				</div>
				
				<div v-else-if="!estimatedSize.valid" class="status-msg error">
				   <span style="color: #f44336;" v-html="'' + estimatedSize.msg"></span>
				</div>
	
				<div v-else class="status-msg ready">
				   <span>Estimated Size:</span>
				   <strong :style="{ color: sizeColor }">{{ Math.round(estimatedSize.sizeMB) }} MB</strong>
				</div>
			</div>
			
			<button 
			  class="modern-btn" 
			  @click="downloadCube" 
			  :disabled="!isReady || isDownloading || !estimatedSize.valid"
			  :class="{ 'btn-loading': isDownloading }"
			>
			  <span v-if="isDownloading" class="spinner-small"></span>
			  <span v-else>
				{{ estimatedSize > 500 ? 'Request via Email' : 'Download NetCDF' }}
			  </span>
			</button>
		  </div>

		</div>
	  </div>
	
  </div>
  
  <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
      <div class="modal-content">
        <button class="modal-close" @click="showHelp = false">&times;</button>
        
        <h2>How to use SHIVER - Data Cube Extractor</h2>
        
        <div class="modal-body">
          <h3>1. Basic Usage</h3>
          <p>
			The Data Cube Extractor allows you to extract a grid of our 
			velocity data covering any area and time-period in which we have observations.
            Use the tools on the left or upload (
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
				<polyline points="17 8 12 3 7 8" />
				<line x1="12" y1="3" x2="12" y2="15" />
			</svg>
			) a file to choose your extraction location. You may only select one extraction area
			at a time. 
			You can also choose the time period, temporal frequency and variables to extract.
          </p>
		  <p>
			Navigate to your preferred ice sheet by clicking the Greenland button 
			( <greenlandIcon class="inline-icon"/> )
			or the Antarctica button
			( <antarcticaIcon class="inline-icon"/> )
		  </p>
		  
		  <h3>2. About the data</h3>
          <p>
            This interactive map lets you extract data cubes of ice velocity in West Greenland and the Antarctic Peninsula.
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
			We provide the data at two quality levels: 'Raw' and 'Time-filtered'. For both quality levels, we have attempted to remove erroneous velocity measurements 
			whilst preserving estimates that do represent the true ice surface velocity. The 'Raw' data has had fewer outliers removed, whilst the 'Time-filtered' data
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
		  
          <h3>3. Uploading Files   
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="17 8 12 3 7 8" />
					<line x1="12" y1="3" x2="12" y2="15" />
				</svg>
		  </h3>
		  <p>
			You can upload a file by clicking the
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
				<polyline points="17 8 12 3 7 8" />
				<line x1="12" y1="3" x2="12" y2="15" />
			</svg>
			symbol.
		  </p>
          <p>
            <strong>Requirements:</strong>
          </p>
          <ul>
            <li><strong>Format:</strong> KMZ, KML, GeoJSON or a zipped shapefile (containing .shp, .shx, .dbf, and .prj files).</li>
            <li><strong>Projection:</strong> Must be in WGS84 (EPSG:4326) .</li>
            <li><strong>Type:</strong> Polygon or Polyline geometries defining a single shape.</li>
          </ul>
		  
          <h3>4. Interpreting the Map</h3>
		  <p>
			When you draw or upload an extraction region, it will be displayed as a yellow polygon. You can edit the shape of the polygon, rotate it
			or remove it using the tools on the left. 
		  </p>
          <p>
            Use the layer controls in the top-left to toggle between <strong>Velocity</strong>, 
            <strong>Measurement Count</strong>, and <strong>Speed Trend</strong>. You can
			optionally overlay ice flow direction arrows and topography data.
		  </p>
		  <ul>
            <li><strong>Topography:</strong> A hillshaded digital elevation model of the area.</li>
            <li><strong>Speed:</strong> The average ice speed between October 2014 and November 2025, in metres per year.</li>
            <li><strong>Measurement count:</strong> The number of valid speed measurements available in each location, espressed as a percentage of the total number of measurements attempted in each location.</li>
			<li><strong>Speed Trend:</strong> The linear trend in speed from October 2014 through November 2025, in metres per year per year.</li>
			<li><strong>Flow direction arrows:</strong> The direction and magnitude of ice flow averaged between October 2014 and November 2025.</li>
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
		  
		  <h3>5. Output</h3>
		  <p>
		    The retrieved data cubes will be in NetCDF format. 
			Large files will be generated offline and a link emailed to you once they are prepared.
		  </p>
		  <p>
            <strong>NetCDF naming convention:</strong> <br>
			IceSheet_Frequency_StartTime_EndTime.nc <br>
			e.g., Greenland_native_2018-01-01_2018-03-31.nc <br>
			Is a data cube for Greenland at the 'native' temporal resolution of the Sentinel-1 measurements from the 1st of January 2018 to the 31st of March 2018.
		  </p>
		  <p>
			<strong>Each NetCDF file could contain contain:</strong>
			<br>
			<em>Note: Only "x", "y", and "time" are exported by default. 
			Other exported variables depend on the selected options. </em>
		  </p>
		  <ul>
            <li><strong>x:</strong> The easting coordinates of the grid, in the local projection.</li>
			<li><strong>y:</strong> The northing coordinates of the grid, in the local projection.</li>
			<li><strong>time:</strong> The date of the measurement. For exports at the 'native' resolution, this represents the mid-date of the measurement epoch. For exports at other temporal resolution, this will be the beginning of the averaging period.</li>
            <li><strong>Date:</strong> The central date of the two images used to estimate ice speed.</li>
            <li><strong>s_error:</strong> An estimate of the global uncertainty in ice speed at this time period. Defined as the median speed over bedrock regions at that time. If data are exported at a resolution other than native, then the mean error over the aggregation period is provided.</li>
			<li><strong>u_error:</strong> An estimate of the global uncertainty in the easting ice velocity at this time period. Defined as the median easting velocity over bedrock regions at that time. If data are exported at a resolution other than native, then the mean error over the aggregation period is provided.</li>
			<li><strong>v_error:</strong> An estimate of the global uncertainty in the northing ice velocity at this time period. Defined as the median northing velocity over bedrock regions at that time. If data are exported at a resolution other than native, then the mean error over the aggregation period is provided.</li>
			<li><strong>s_filt:</strong> Horizontal ice surface speed in metres per year, from the time-filtered zarr store variable.</li>
			<li><strong>s_raw:</strong> Horizontal ice surface speed in metres per year, from the raw (no time filtering) zarr store variable.</li>
			<li><strong>u_filt:</strong> Horizontal  ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the time-filtered zarr store variable.</li>
			<li><strong>u_raw:</strong> Horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the raw (no time filtering) zarr store variable.</li>
			<li><strong>v_filt:</strong> Horizontal  ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the time-filtered zarr store variable.</li>
			<li><strong>v_raw:</strong> Horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the raw (no time filtering) zarr store variable.</li>
          </ul>
		  <p>
			<em>If the data are exported at the native temporal resolution, there is an additional variable:</em>
		  </p>
		  <ul>
            <li><strong>Time_separation_days:</strong> The number of days between the two images used to estimate ice speed. So the first image was acquired on Date-Time_separation_days/2, and the second image on Date+Time_separation_days/2.</li>
		  </ul>
		  <p>
			<em>If the data are exported any temporal resolution other than native, then we also provide the standard deviation of each variable during each aggregation period and the count of non-nan measurements during each aggregation period:</em>
		  </p>
		  <ul>
            <li><strong>s_error_std:</strong> The standard deviation of the global uncertainty in ice speed during the aggregation period.</li>
			<li><strong>u_error_std:</strong> The standard deviation of the global uncertainty in the easting ice velocity during the aggregation period.</li>
			<li><strong>v_error_std:</strong> The standard deviation of the global uncertainty in the northing ice velocity during the aggregation period.</li>
			<li><strong>s_filt_std:</strong> The standard deviation of the horizontal ice surface speed in metres per year, from the time-filtered zarr store variable.</li>
			<li><strong>s_raw_std:</strong> The standard deviation fo the horizontal ice surface speed in metres per year, from the raw (no time filtering) zarr store variable.</li>
			<li><strong>u_filt_std:</strong> The standard deviation of the horizontal  ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the time-filtered zarr store variable.</li>
			<li><strong>u_raw_std:</strong> The standard deviation of the horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the raw (no time filtering) zarr store variable.</li>
			<li><strong>v_filt_std:</strong> The standard deviation of the horizontal  ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the time-filtered zarr store variable.</li>
			<li><strong>v_raw_std:</strong> The standard deviation of the horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the raw (no time filtering) zarr store variable.</li>
			<li><strong>measurement_count:</strong> The number of non-nan measurements in each aggregation period.</li>
		  </ul>
        </div>
      </div>
    </div>
	
</template>

<script setup>
// --- IMPORTS ---
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue';
import { LMap, LTileLayer, LGeoJson, LControlLayers, LLayerGroup, LControlScale, LTooltip } from "@vue-leaflet/vue-leaflet";
import axios from 'axios';
import { saveAs } from 'file-saver';
import L from 'leaflet';
import antarcticaIcon from '../components/icons/antarcticaIcon.vue';
import greenlandIcon from '../components/icons/greenlandIcon.vue';
import "@geoman-io/leaflet-geoman-free";
import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import "leaflet/dist/leaflet.css";
import * as turf from '@turf/turf';
import { differenceInWeeks, differenceInMonths, differenceInYears } from 'date-fns'; // useful for time steps
import { useAuthStore } from '../stores/auth';
import shp from 'shpjs';
import toGeoJSON from '@mapbox/togeojson'; // For KML
import JSZip from 'jszip'; // For KMZ

// --- API CONFIGURATION ---
import apiClient, { API_URL } from '../api';


// --- NATIVE GOOGLE ANALYTICS TRACKING ---
const trackEvent = (eventName, params = {}) => {
  if (typeof window.gtag === 'function') {
    window.gtag('event', eventName, params);
    console.log(`?? GA Event Sent: ${eventName}`, params);
  } else {
    console.log(`?? GA Event Skipped (Not loaded): ${eventName}`);
  }
};


// --- FEEDBACK POPUP STATE ---
// The main trigger function
const triggerFeedbackPopup = () => {
  const hasShown = sessionStorage.getItem(STORAGE_KEY);
  if (!hasShown) {
    showFeedbackPopup.value = true;
    sessionStorage.setItem(STORAGE_KEY, 'true');
    cleanupTriggers();  // Once triggered, we can stop listening for exit intent or time
  }
};

// Exit Intent Handler
const handleExitIntent = (event) => {
  // We check if clientY <= 0. This detects if the mouse moves OUT 
  // of the top of the viewport (towards tabs/address bar).
  // This prevents the popup from showing if they just move the mouse 
  // to a second monitor on the right/left.
  if (event.clientY <= 0) {
    triggerFeedbackPopup();
  }
};

const closeFeedbackPopup = () => {
  showFeedbackPopup.value = false;
};

// Clean up listeners to prevent memory leaks or errors
const cleanupTriggers = () => {
  if (timerInstance) clearTimeout(timerInstance);
  document.removeEventListener('mouseleave', handleExitIntent);
};

onMounted(() => {
  // Check immediately if we've already shown it this session (e.g. on page refresh)
  // If yes, do nothing. If no, start the listeners.
  if (!sessionStorage.getItem(STORAGE_KEY)) {
    // 1. Set the time-based trigger
    timerInstance = setTimeout(() => {
      triggerFeedbackPopup();
    }, TIME_DELAY_MS);
    // 2. Set the exit-intent trigger
    document.addEventListener('mouseleave', handleExitIntent);
  }
});

onUnmounted(() => {
  cleanupTriggers(); // Good practice to clean up when the component is destroyed
});



// --- REACTIVE STATE ---
const map = ref(null);
const currentRegion = ref('Greenland');
const overlayLayer = ref('none'); // Tracks which visual layer is active (speed/count/trend)
const zoom = ref(8);
const center = ref([67.133129, -48.900752]);
const statusMessage = ref("");
const statusType = ref("");
const isDragging = ref(false);
const isUploading = ref(false);
const glacierData = ref(null);
const glacierNamesData = ref(null);
const showHelp = ref(false); 
const iceEdgeData = ref(null);
const groundingLineData = ref(null);
const showMargins = ref(false);
const mapHeightPercent = ref(70); 
const isFlowActive = ref(false);
const isHillshadeActive = ref(false);
const globalMaskData = ref(null);
const globalOutlineData = ref(null);
const legendItems = ref([]);
const isUserZoomed = ref(false);
const TIME_DELAY_MS = 90000; // 1.5 Minutes 
const STORAGE_KEY = 'shiver_feedback_shown';
const showFeedbackPopup = ref(false);
const isMessageSpinnerRequired = ref(false);  // Optional: controls the spinner
const drawnLayer = ref(null);
const geoUpdateTrigger = ref(0);
const fileInput = ref(null);
const isDownloading = ref(false);
const auth = useAuthStore();
let leafletMap = null;
let timerInstance = null;
let messageTimeout = null;

// Cube Parameters
const startDate = ref('2018-01-01');
const endDate = ref('2018-12-31');
const frequency = ref('monthly');
const selectedVariables = ref(['s_filt']);

// Cube limits
const MAX_SPATIAL_PIXELS = 250000;
const MAX_AREA_SQM = 10000000000; // 10,000 sq km
const MAX_VOLUME_MB = 2000;

const availableVariables = [
  { id: 's_filt', name: 'Speed (Time-filtered)' },
  { id: 'u_filt', name: 'U Velocity (Time-filtered)' },
  { id: 'v_filt', name: 'V Velocity (Time-filtered)' },
  { id: 's_raw', name: 'Speed (Raw)' },
  { id: 'u_raw', name: 'U Velocity (Raw)' },
  { id: 'v_raw', name: 'V Velocity (Raw)' },
];

// Computed parameters
const isRegionDrawn = computed(() => !!drawnLayer.value);
const isReady = computed(() => isRegionDrawn.value && selectedVariables.value.length > 0);


//----------------------------------------------------------------------------
// -------------------//
// --- Geoman setup --- //
// ------------------ //
const onMapReady = (mapInstance) => {

  // Sometimes Vue-Leaflet returns the component (mapInstance), 
  // sometimes the map itself. We check for 'leafletObject'.
  const map = mapInstance.leafletObject || mapInstance;
  
  // Save a copy of the map for later
  leafletMap = map;
  
  // Ensure Geoman loaded
  if (!map.pm) {
    console.error("Geoman plugin not attached to map instance.");
    return;
  }
  
  // A. Add Controls
  map.pm.addControls({
    position: 'topleft',
    drawCircle: false,
    drawMarker: false,
    drawCircleMarker: false,
    drawPolyline: false,
    drawPolygon: true,
    drawRectangle: true,
    editMode: true,
    dragMode: false, 
    cutPolygon: false,
    removalMode: true,
	drawText: false,
  });

  // B. Enforce Single Shape Logic & Styling
  map.on('pm:create', (e) => {
    // If a shape already exists, remove it
    if (drawnLayer.value) {
      map.removeLayer(drawnLayer.value);
    }
    
    // Save the new layer to our Vue ref
    drawnLayer.value = e.layer;
    
    // Style it (Yellow dashed line)
    e.layer.setStyle({ 
        color: '#ffeb3b', 
        weight: 2, 
        fillOpacity: 0.2, 
        dashArray: '5, 5' 
    });
    
    // Listen for removal (e.g. if user clicks the trash can)
    e.layer.on('remove', () => { 
        drawnLayer.value = null; 
    });
	
	// Check when vertices are moved or added
    e.layer.on('pm:edit', () => {
        geoUpdateTrigger.value++;
    });

    // Check when the whole polygon is dragged
    e.layer.on('pm:dragend', () => {
        geoUpdateTrigger.value++;
    });
    
    // Check if a section is cut 
    e.layer.on('pm:cut', () => {
        geoUpdateTrigger.value++;
    });
  });
  
  // C. Optional: Handle "Cut" or "Edit" events if you need to update the ref
  map.on('pm:remove', () => {
      drawnLayer.value = null;
  });
};



//----------------------- //
// --- CUBE GENERATION --- //
// --------------------- //
const downloadCube = async () => {
  if (!drawnLayer.value) {
    setStatus('Error: Please draw a region first.', 'error');
    return;
  }

  isDownloading.value = true;
  setStatus('Processing request...', 'loading');

  try {
    const geojson = drawnLayer.value.toGeoJSON();
    
    // Handle Rectangle vs Polygon structure
    const geometry = geojson.geometry ? geojson.geometry : geojson;

    const payload = {
      roi_geojson: geometry,
      date_start: startDate.value,
      date_end: endDate.value,
      variables: selectedVariables.value,
      frequency: frequency.value
    };

    // We request 'blob' because 90% of the time it will be a file.
    // If it is JSON (202 Accepted), we will convert the blob to text manually.
    const response = await apiClient.post('/api/cube/download', payload, {
      responseType: 'blob', 
      headers: { 
        'Authorization': `Bearer ${auth.token}` 
      }
    });

    // --- CASE 1: LARGE FILE (Background Processing) ---
    if (response.status === 202) {
      // The response is a Blob containing JSON. Convert it to text.
      const textData = await response.data.text(); 
      const jsonData = JSON.parse(textData);
      setStatus('Request Accepted: Check your email.', 'success');
      return; // Stop here, do not try to download
    }

    // --- CASE 2: SMALL FILE (Direct Download) ---
    if (response.status === 200) {

        // 1. Robust Filename Extraction
        let filename = 'cube.nc'; // Fallback
        
        // Headers can be case-insensitive, so we check carefully
        const disposition = response.headers['content-disposition'];

        if (disposition && disposition.indexOf('attachment') !== -1) {
            // Regex to match filename="name" or filename=name
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(disposition);
            if (matches != null && matches[1]) { 
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // 2. Create Download Blob
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        
        // 3. Use the extracted filename
        link.setAttribute('download', filename);
        
        document.body.appendChild(link);
        link.click();
        
        // Cleanup
        link.remove();
        window.URL.revokeObjectURL(url);
        
        setStatus(`Download Started: ${filename}`, 'success'); // Changed to 'success' (green)
    }

  } catch (error) {
    console.error(error);
    let msg = "Server Error";

    // Handle Blob Errors (since responseType was 'blob', errors are also blobs)
    if (error.response && error.response.data) {
        try {
            // Convert Blob error to text
            const text = await error.response.data.text();
            const json = JSON.parse(text);
            msg = json.detail || json.message;
        } catch(e) {
            // If parsing fails, use default message
        }
        
        // Handle 401 Unauthorized specifically
        if (error.response.status === 401) {
            msg = "Session expired. Please log in again.";
            auth.logout();
            router.push('/login');
        }
    }
    
    setStatus(`Error: ${msg}`, 'error');
  } finally {
    isDownloading.value = false;
  }
};

const setStatus = (msg, type) => {
  statusMessage.value = msg;
  statusType.value = type;
  
  // Clear message after 5 seconds unless it's a persistent state
  if (type !== 'loading' && type !== 'error') {
    setTimeout(() => {
        statusMessage.value = '';
        statusType.value = '';
    }, 5000);
  }
};



//---------------------- //
// --- SIZE ESTIMATION --- //
// -------------------- //
const estimatedSize = computed(() => {
  geoUpdateTrigger.value; // Re-run function if this value changes
  // Default "Empty" State
  const result = { sizeMB: 0, valid: true, msg: '' };

  if (!drawnLayer.value || !startDate.value || !endDate.value) return result;

  try {
    // 1. Calculate Area (Leaflet -> GeoJSON -> Turf)
    const geojson = drawnLayer.value.toGeoJSON();
    const areaSqMeters = turf.area(geojson);

    // 2. Determine Resolution & Pixel Count
    const pixelSizeX = 200; 
    const pixelSizeY = 200;
    const areaPerPixel = pixelSizeX * pixelSizeY;
    const numSpatialPixels = areaSqMeters / areaPerPixel;

    // Check size
    if (numSpatialPixels > MAX_SPATIAL_PIXELS || areaSqMeters > MAX_AREA_SQM) {
        const areaKm = (areaSqMeters / 1e6).toFixed(0);
        return {
            sizeMB: 0, 
            valid: false, 
            msg: `Area too large (${areaKm} km&sup2;). Max is 10,000 km&sup2;.` 
        };
    }

    // 3. Calculate Time Steps
    const start = new Date(startDate.value);
    const end = new Date(endDate.value);
    let timeSteps = 1;

    // (Your existing frequency logic...)
    if (frequency.value === 'native') {
        timeSteps = Math.max(1, differenceInWeeks(end, start) * 6);
    } else if (frequency.value === 'monthly') {
        timeSteps = Math.max(1, differenceInMonths(end, start) * 2);
    } else if (frequency.value === 'quarterly') {
        timeSteps = Math.max(1, differenceInMonths(end, start) * 2 / 3);
    } else if (frequency.value === 'annual') {
        timeSteps = Math.max(1, differenceInYears(end, start) * 2);
    }

    // 4. Variables
    const numVars = selectedVariables.value.length || 1; // Prevent 0 div errors

    // 5. Total Bytes
    const totalBytes = numSpatialPixels * timeSteps * numVars * 4;
    const sizeMB = totalBytes / (1024 * 1024);

    // Check volume 
    if (sizeMB > MAX_VOLUME_MB) {
        return {
            sizeMB: sizeMB,
            valid: false,
            msg: `Volume (${sizeMB.toFixed(0)} MB) exceeds 2GB limit.`
        };
    }

    // Success
    return { sizeMB: sizeMB, valid: true, msg: '' };

  } catch (e) {
    console.error(e);
    return { sizeMB: 0, valid: false, msg: 'Calculation Error' };
  }
});

// Helper for UI Color
const sizeColor = computed(() => {
  // 1. If Invalid, show Red (Error color)
  if (!estimatedSize.value.valid) return '#f44336'; 

  // 2. Get the number
  const size = estimatedSize.value.sizeMB;

  // 3. Standard Logic
  if (size < 100) return '#4caf50'; // Green (Small)
  if (size < 500) return '#ffeb3b'; // Yellow (Medium)
  return '#f44336'; // Red (Large)
});


//--------------------------------------------------------------------------------------------
//--------------------------//
// --- FILE UPLOAD ---//
//-------------------------//
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  isUploading.value = true;
  setStatus('Parsing file...', 'loading');

  try {
    const fileName = file.name.toLowerCase();
    let geojson = null;

    // --- CASE A: GeoJSON ---
    if (fileName.endsWith('.geojson') || fileName.endsWith('.json')) {
      const text = await file.text();
      geojson = JSON.parse(text);
    } 
    // --- CASE B: Zipped Shapefile (.zip) ---
    else if (fileName.endsWith('.zip')) {
      const buffer = await file.arrayBuffer();
      geojson = await shp(buffer);
    } 
    // --- CASE C: KML (.kml) ---
    else if (fileName.endsWith('.kml')) {
      const text = await file.text();
      const parser = new DOMParser();
      const kmlDom = parser.parseFromString(text, 'text/xml');
      geojson = toGeoJSON.kml(kmlDom);
    } 
    // --- CASE D: KMZ (.kmz) ---
    else if (fileName.endsWith('.kmz')) {
      const buffer = await file.arrayBuffer();
      const zip = await JSZip.loadAsync(buffer);
      
      // Find the first .kml file inside the zip
      const kmlFile = Object.keys(zip.files).find(n => n.endsWith('.kml'));
      if (!kmlFile) throw new Error("No KML file found inside KMZ");
      
      const kmlString = await zip.file(kmlFile).async('string');
      const parser = new DOMParser();
      const kmlDom = parser.parseFromString(kmlString, 'text/xml');
      geojson = toGeoJSON.kml(kmlDom);
    } 
    else {
      throw new Error("Unsupported file format. Please use .zip (Shapefile), .geojson, .kml, or .kmz");
    }

    // --- VALIDATION & CLEANUP ---
    // Handle FeatureCollections (take the first feature) or Arrays
    if (Array.isArray(geojson)) {
      // shpjs sometimes returns an array of feature collections
      geojson = geojson[0]; 
    }
    
    // Normalize to a single feature if it's a FeatureCollection
    if (geojson.type === 'FeatureCollection') {
        if (geojson.features.length === 0) throw new Error("File contains no geometries.");
        // Merge or just take the first one? 
        // For simplicity, let's take the first feature, as requested.
        geojson = geojson.features[0];
    }

    // --- DRAW ON MAP ---
    drawGeoJSONOnMap(geojson);
    setStatus('File uploaded successfully', 'success');

  } catch (error) {
    console.error(error);
    setStatus(`Upload Failed: ${error.message}`, 'error');
  } finally {
    isUploading.value = false;
    // Reset the input so the same file can be selected again if needed
    event.target.value = ''; 
  }
};

// --- HELPER TO RENDER ON LEAFLET ---
const drawGeoJSONOnMap = (geojsonFeature) => {
  // Safety check: ensure map is loaded
  if (!leafletMap) {
      console.error("Map not ready yet.");
      return;
  }

  // A. Remove existing layer (Duplicate your 'pm:create' logic)
  if (drawnLayer.value) {
    leafletMap.removeLayer(drawnLayer.value);
    drawnLayer.value = null;
  }

  // B. Parse the GeoJSON
  // L.geoJSON returns a LayerGroup, but we want the specific polygon inside
  const tempLayer = L.geoJSON(geojsonFeature);
  const layers = tempLayer.getLayers();
  
  if (layers.length === 0) return;
  
  const newLayer = layers[0]; // Take the first shape found

  // C. Apply your specific Yellow Dashed Styling
  if (newLayer.setStyle) {
      newLayer.setStyle({ 
        color: '#ffeb3b', 
        weight: 2, 
        fillOpacity: 0.2, 
        dashArray: '5, 5' 
      });
  }

  // D. Add to Map and Update State
  newLayer.addTo(leafletMap);
  drawnLayer.value = newLayer;

  // E. Attach the 'remove' listener (So the X button works)
  newLayer.on('remove', () => { 
      drawnLayer.value = null; 
  });
  
  // F. Enable Geoman editing on this new imported shape
  // (This allows the user to click the edit button on the imported file)
  if (newLayer.pm) {
      newLayer.pm.enable(); // Optional: Turn on edit mode immediately
      newLayer.pm.disable(); // Or just register it but keep it disabled
  }

  // G. Fly to the new location
  leafletMap.fitBounds(newLayer.getBounds(), { padding: [50, 50] });
};




//--------------------------------------------------------------------------------------------
//--------------------------//
// --- MASKS AND OVERLAYS ---//
//-------------------------//

// --- Good data mask --- //
onMounted(async () => {
  try {
    const [maskRes, outlineRes] = await Promise.all([
      apiClient.get('/static/global_data_mask.geojson'),
      apiClient.get('/static/data_outlines.geojson')
    ]);
    // Axios puts the actual JSON content inside the .data property
    globalMaskData.value = maskRes.data;
    globalOutlineData.value = outlineRes.data;
  } catch (e) { console.error("Data boundary loading failed.", e); }
});


// Vectors
const REFERENCE_VELOCITY = computed(() => {
  if (currentRegion.value === 'Greenland') {
    return 250; // Greenland Legend shows 250 m/yr
  } else {
    return 500; // Antarctica Legend shows 500 m/yr (since scale is 5000 vs 2250)
  }
});
const TILE_SIZE = 256; 
const vectorScaleLabel = computed(() => { return `${REFERENCE_VELOCITY.value} m/yr`; });
const arrowPixelWidth = computed(() => {
  if (!currentRegion.value) return 50; 
  // Backend Scales: Greenland=2250, Antarctica=5000
  const scale = currentRegion.value === 'Greenland' ? 2250 : 5000;
  // Math: (1000 / Scale) * 256
  // Greenland result: ~113px
  // Antarctica result: ~51px
  return (REFERENCE_VELOCITY.value / scale) * TILE_SIZE;
});



// --- WATCHER FOR STATUS MESSAGE --- //
watch(statusMessage, (newVal) => {
  // 1. Clear any existing timer so we don't fade out prematurely
  if (messageTimeout) clearTimeout(messageTimeout);

  // 2. If message is cleared externally, do nothing
  if (!newVal) return;

  // 3. Logic: If it looks like a "completion" message, set a timer to hide it.
  //    If it looks like a "processing" message (ends in '...'), keep it visible.
  if (!newVal.endsWith('...')) {
      isMessageSpinnerRequired.value = false; // Stop spinner
      
      // Auto-hide after 2.5 seconds
      messageTimeout = setTimeout(() => {
          statusMessage.value = "";
      }, 2500);
  } else {
      isMessageSpinnerRequired.value = true; // Start spinner
  }
});





// -----------------------------//
// --- LEGEND & LAYER LOGIC --- //
// ---------------------------- //
// --- COMPUTED URLs FOR TILES ---
const timestamp = computed(() => Date.now()); 
const baseUrl = API_URL.replace(/\/$/, '');
const speedUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/speed/{z}/{x}/{y}.png?t=${timestamp.value}`);
const countUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/count/{z}/{x}/{y}.png?t=${timestamp.value}`);
const trendUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/trend/{z}/{x}/{y}.png?t=${timestamp.value}`);
const vectorUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/vectors/{z}/{x}/{y}.png?t=${timestamp.value}` );
const hillshadeUrl = computed(() => `${baseUrl}/api/tiles/${currentRegion.value}/hillshade/{z}/{x}/{y}.png?t=${timestamp.value}` );

// Leaflet's <l-control-layers> handles the actual map toggling.
// These events listen to Leaflet to update our local 'overlayLayer' state,
// which determines which Legend bar to show in the bottom right.
const iceEdgeStyle = { color: "black", weight: 2 };
const groundingLineStyle = { color: "magenta", weight: 2 };

const onOverlayAdd = (e) => {  
  const rasterLayers = ['Ice Speed', 'Measurement Count', 'Speed Trend', 'Topography', 'Flow direction arrows'];
  if (rasterLayers.includes(e.name)) {
    // If clicking a raster layer, switch the active raster
	if (e.name === 'Ice Speed') overlayLayer.value = 'speed';
    if (e.name === 'Measurement Count') overlayLayer.value = 'count';
    if (e.name === 'Speed Trend') overlayLayer.value = 'trend';
	if (e.name === 'Topography') isHillshadeActive.value = true;
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
  if (e.name === "Topography") isHillshadeActive.value = false; 
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
const maxSpeedLabel = computed(() => currentRegion.value === 'Greenland' ? '400 m/yr' : '2000 m/yr');
const maxTrendLabel = computed(() => currentRegion.value === 'Greenland' ? '2.5' : '15');
const minTrendLabel = computed(() => currentRegion.value === 'Greenland' ? '-2.5' : '-15');


// ----------------------------
// --- REGION MANAGEMENT --- //
// ----------------------------
const switchRegion = () => {
  if (currentRegion.value === 'Greenland') {
    center.value = [67.133129, -48.900752]; zoom.value = 8;
  } else {
    center.value = [-66.323903, -63.355695]; zoom.value = 6;
  }
  // Force Leaflet to fly to the new center
  if (map.value && map.value.leafletObject) map.value.leafletObject.setView(center.value, zoom.value);
};


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



//--------------------------------------------------------------------------------------------
//--------------------------//
// --- DRAG BAR ---//
//-------------------------//
const startDrag = (e) => {
  if (e.cancelable) e.preventDefault();
  isDragging.value = true;
  // Change the cursor for the whole body so it doesn't flicker if you drag fast
  document.body.style.cursor = 'row-resize';
  // Prevent text selection highlighting while dragging
  document.body.style.userSelect = 'none';
  // Attach listeners to window so dragging continues even if mouse leaves the handle
  window.addEventListener('mousemove', onDrag);
  window.addEventListener('mouseup', stopDrag);
  // Attach Touch Listeners (passive: false allows us to prevent scrolling)
  window.addEventListener('touchmove', onDrag, { passive: false });
  window.addEventListener('touchend', stopDrag);
};

const onDrag = (e) => {
  if (!isDragging.value) return;
  
  // 1. Get Client Y (Unified for Mouse & Touch)
  let currentY; 
  if (e.type.includes('touch')) {
      // Touch Event: clientY is nested inside touches[0]
      currentY = e.touches[0].clientY;
      
      // Prevent scrolling the page while dragging
      if (e.cancelable) e.preventDefault(); 
  } else {
      // Mouse Event: clientY is on the root event
      currentY = e.clientY;
  }

  const container = document.querySelector('.page-container');
  if (!container) return;

  // 2. Calculate position relative to container
  const containerRect = container.getBoundingClientRect();
  const relativeY = currentY - containerRect.top;
  
  // Convert to percentage
  let newHeight = (relativeY / containerRect.height) * 100;

  // Clamp limits (e.g., Map can't be smaller than 10% or larger than 90%)
  newHeight = Math.min(Math.max(newHeight, 10), 90);
  mapHeightPercent.value = newHeight;

  // Trigger redraw of plotly and leaflet
  window.dispatchEvent(new Event('resize'));
};

const stopDrag = () => {
  isDragging.value = false;
  // Revert cursor and text selection to default
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  // Remove Mouse Listeners
  window.removeEventListener('mousemove', onDrag);
  window.removeEventListener('mouseup', stopDrag);
  // Remove Touch Listeners
  window.removeEventListener('touchmove', onDrag);
  window.removeEventListener('touchend', stopDrag);
  // Final resize trigger to ensure crisp rendering
  setTimeout(() => window.dispatchEvent(new Event('resize')), 100);
};


</script>

<style scoped>
/* --- MAIN LAYOUT --- */
.page-container { display: flex; flex-direction: column; height: calc(100vh - 60px); width: 100%; overflow: hidden; }
.map-wrapper { position: relative; width: 100%; user-select: none; container-type: size; container-name: map-container }

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
  position: relative;
  touch-action: none;
}

/* Add an invisible touch target, to make it easier to hit on a phone */
.resize-handle::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: -15px;    /* Extend 15px Up */
  bottom: -15px; /* Extend 15px Down */
  z-index: 2001; /* Sit on top of everything */
  cursor: row-resize;
}

.resize-handle:hover { background-color: #e0e0e0; }

/* The little visual "grip" lines in the middle */
.handle-grip { width: 40px; height: 4px; border-top: 2px solid #999; border-bottom: 2px solid #999; }


/* --- MAIN CONTROLS--- */ 
.map-toolbar {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000; /* Above Leaflet Map */
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* The wrapper holds the actual button groups */
.tools-wrapper {
  display: flex;
  flex-direction: column;
  gap: 15px;
  transition: opacity 0.2s ease;
}

.toolbar-group {
  display: flex;
  flex-direction: column;
  gap: 8px; /* Space between buttons in a group */
  background: rgba(255, 255, 255, 0.9);
  padding: 8px;
  border-radius: 20px; /* Capsule shape container */
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  backdrop-filter: blur(4px);
}

/* The Hamburger Menu Button (Hidden by default) */
.menu-trigger {
  display: none; 
  margin-bottom: 10px;
}
.menu-trigger .panel-btn {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 6px rgba(0,0,0,0.15);
  width: 40px;
  height: 40px;
  border-radius: 50%; /* Circle shape for the trigger */
}

/* --- RESPONSIVE LOGIC --- */
/* If the screen height is less than 750px, switch to Compact Mode */
@container map-container (height < 500px) {
  
  /* 1. Show the hamburger button */
  .menu-trigger {
    display: block;
  }

  /* 2. Hide the tools by default */
  .tools-wrapper {
    /* Hidden state */
    opacity: 0;
    visibility: hidden; /* Use visibility instead of pointer-events */
    position: absolute;
    top: 0;
    right: 50px;
    flex-direction: row-reverse; 
    align-items: flex-start;
    /* pretty transition */
    transition: 
      opacity 0.3s ease 0.5s, 
      visibility 0s linear 0.8s;
  }

  /* 3. On Hover: Reveal the tools */
  .map-toolbar:hover .tools-wrapper {
    opacity: 1;
    visibility: visible;
    transition: 
      opacity 0.2s ease 0s, 
      visibility 0s linear 0s;
  }
}
.region-toggles, .header-actions {
  display: flex;
  gap: 12px; /* Space between buttons */
}

.panel-btn {
  width: 45px;
  height: 45px;
  border-radius: 50%; /* Makes them perfectly circular */
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;       /* White background by default */
  border: 1px solid #ddd; /* Subtle grey border */
  color: #555;            /* Grey icon/text */
  font-size: 1.25rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

/* Update .panel-btn to handle SVGs with strokes (like the upload icon) */
.panel-btn svg {
  fill: currentColor; 
  stroke: currentColor; 
}

/* Ensure the fill-based icons (like the Gear) don't get messed up by stroke */
.panel-btn svg[fill="currentColor"] {
  stroke: none;
}

.panel-btn svg path[stroke="#2c3e50"] {
  stroke: currentColor; /* Matches the button text color (grey or white) */
  fill: transparent;
}

.inline-icon {
  display: inline-block;
  height: 3.0em;       /* Scales relative to the font size (makes it fit) */
  width: auto;         /* Maintains aspect ratio */
  vertical-align: middle; /* Aligns center of icon with center of lowercase text */
  margin: 0 0px;       /* Adds a tiny bit of breathing room */
  position: relative;  
  top: -2px;           /* visual tweak to lift it slightly if needed */
  fill: currentColor;  /* Optional: makes the icon take the text color */
}

/* A smaller spinner specifically for inside the buttons */
.spinner-small {
  display: inline-block;
  width: 14px;  /* Fits nicely inside the 32px button */
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff; /* White spinner looks great on the blue active background */
  animation: spin 0.8s linear infinite;
}

/* (Make sure you still have your @keyframes spin defined from before!) */
@keyframes spin { to { transform: rotate(360deg); } }

/* HOVER STATE (When mouse is over) */
.panel-btn:hover {
  border-color: #888;     /* Darker border */
  color: #333;            /* Darker text */
  background: #f8f9fa;    /* Very light grey fill */
}

/* ACTIVE STATE (Selected Region or Open Menu) */
.panel-btn.active {
  background: #2c3e50;    /* Dark Blue fill */
  border-color: #2c3e50;  /* match fill */
  color: #fff;            /* White text/icon */
}

/* Ensure disabled buttons look inactive */
.panel-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f0f0f0;
}


/*------------------------------------*/
/* --- 2. BOTTOM DASHBOARD LAYOUT --- */
/*------------------------------------*/
.cube-controls {
  background: #1a2634;
  color: #e0e6ed;
  padding: 0; /* Padding moved to inner elements for better scroll control */
  display: flex;
  flex-direction: column;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.3);
  border-top: 1px solid #2c3e50;
  overflow: hidden; /* Prevent double scrollbars */
  transition: height 0.3s ease;
}

.controls-header {
  padding: 15px 25px;
  background: rgba(0,0,0,0.2);
  border-bottom: 1px solid #2c3e50;
  flex-shrink: 0;
}

.controls-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #00ccff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.controls-header .instruction {
  margin: 4px 0 0 0;
  font-size: 0.85rem;
  color: #8b9bb4;
}

/* --- GRID LAYOUT FOR BODY --- */
.controls-body {
  padding: 20px 25px;
  overflow-y: auto; /* Allow scrolling inside controls if screen is short */
  display: grid;
  /* Magic Grid: Columns are at least 300px wide. 
     If space permits, they sit side-by-side (3 columns).
     If space is tight (tablet/mobile), they wrap automatically.
  */
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  align-items: start;
}

/* --- CARDS (COLUMNS) --- */
.control-card {
  background: rgba(255,255,255,0.03);
  padding: 15px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
  display: flex;
  flex-direction: column;
  height: 100%; /* Match height of neighbors */
  container-type: inline-size;
}

.section-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #8b9bb4;
  margin-bottom: 10px;
  font-weight: 700;
}

.mt-3 { margin-top: 15px; }

/* --- INPUTS --- */
.dark-input {
  background: #0b1e3b;
  border: 1px solid #2c3e50;
  color: white;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box; /* Fix padding issues */
}

.dark-input:focus {
  border-color: #00ccff;
  box-shadow: 0 0 0 2px rgba(0, 204, 255, 0.2);
}

.date-row {
  display: flex;
  align-items: flex-end; /* Align inputs */
  gap: 10px;
  flex-wrap: wrap;
}

.input-group {
  flex: 1 1 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
}

.sub-label {
  font-size: 0.75rem;
  color: #6c7a89;
}

.separator {
  padding-bottom: 10px;
  color: #8b9bb4;
  font-weight: bold;
}

@container (max-width: 320px) {
  .separator {
    display: none;
  }
  
  /* Optional: Add a tiny vertical gap when stacked so they don't touch */
  .date-row {
    gap: 8px; 
  }
}

/* --- CUSTOM CHECKBOXES --- */
.checkbox-scroller {
  max-height: 250px;
  overflow-y: auto;
  padding-right: 5px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 6px;
  background: rgba(0,0,0,0.2);
  cursor: pointer;
  transition: background 0.2s;
}

.checkbox-item:hover {
  background: rgba(255,255,255,0.05);
}

.checkbox-item.checked {
  background: rgba(0, 204, 255, 0.1);
  border: 1px solid rgba(0, 204, 255, 0.3);
}

.custom-check {
  width: 16px;
  height: 16px;
  border: 2px solid #556;
  border-radius: 3px;
  display: inline-block;
  position: relative;
}

.checkbox-item.checked .custom-check {
  background: #00ccff;
  border-color: #00ccff;
}

/* Checkmark tick */
.checkbox-item.checked .custom-check::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid #0b1e3b;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.var-name {
  font-size: 0.9rem;
  user-select: none;
}

/* --- ACTION AREA --- */
.action-card {
  justify-content: space-between;
  align-items: center;
  text-align: center;
  background: transparent; /* No bg for action card to look cleaner */
  border: none;
}

.status-area {
  margin-bottom: 15px;
  width: 100%;
}

.status-msg {
  padding: 10px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.status-msg.warning {
  background: rgba(255, 235, 59, 0.1);
  color: #ffeb3b;
  border: 1px solid rgba(255, 235, 59, 0.3);
}

.status-msg.ready {
  background: rgba(0, 255, 150, 0.1);
  color: #00ff96;
  border: 1px solid rgba(0, 255, 150, 0.3);
  display: flex;
  flex-direction: column;
}

.modern-btn {
  background: linear-gradient(135deg, #00ccff 0%, #0088cc 100%);
  color: white;
  border: none;
  padding: 12px 30px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 50px; /* Pill shape */
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 15px rgba(0, 204, 255, 0.3);
  width: 100%;
}

.modern-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 204, 255, 0.4);
}

.modern-btn:disabled {
  background: #2c3e50;
  color: #556;
  box-shadow: none;
  cursor: not-allowed;
}

/* --- MOBILE RESPONSIVENESS --- */
@media (max-width: 768px) {
  .cube-controls {
    /* IMPORTANT: On mobile, 35% height is too small to stack everything.
       We force it to be at least auto-height or fixed larger size.
       Using !important to override the inline style from Vue.
    */
    height: auto !important; 
    min-height: 50%; 
    max-height: 80%; /* Don't cover the whole map */
  }

  .controls-body {
    grid-template-columns: 1fr; /* Force single column stack */
    padding: 15px;
  }
  
  /* Make date inputs stack on very small screens */
  .date-row {
      flex-direction: row; 
  }
}

/* --- BRANDING (SHIVER) --- */
/* --- 1. FLOATING TITLE OVERLAY --- */
.map-title-overlay {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%); /* Centers the div perfectly */
  z-index: 1000; /* Ensures it sits above the map layers */
  
  background: rgba(255, 255, 255, 0.9); /* Semi-transparent white */
  backdrop-filter: blur(4px); /* Nice "frosted glass" effect */
  padding: 10px 25px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  
  text-align: center;
  pointer-events: none; /* Allows clicks to pass through transparent areas */
  border: 1px solid rgba(0,0,0,0.1);
}

.shiver-title {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
  color: #0b1e3b;
  letter-spacing: 1px;
  line-height: 1;
}

.shiver-subtitle {
  font-size: 0.75rem;
  color: #0077B6;
  margin-top: 4px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* mobile resize */
@media (max-width: 768px) {
  .map-title-overlay {
    top: 10px;
    padding: 6px 15px;
    width: 25%; /* Prevent it from being too wide on phones */
  }
  
  .shiver-title {
    font-size: 1.2rem;
  }
  
  .shiver-subtitle {
    display: none; /* Hide subtitle on very small screens to save space */
  }
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

/* --- PAGE BEHAVIOUR --- */
.page-container.is-global-loading,
.page-container.is-global-loading * {
  cursor: wait !important;
}


/* --- MAP LEGEND --- */
.map-legend {
  position: absolute; bottom: 30px; right: 340px; z-index: 999;
  background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2); width: 240px; font-family: sans-serif; pointer-events: none;
}

.legend-container {
  position: absolute;
  bottom: 30px;
  left: 10px;
  z-index: 1000;
  display: flex;
  flex-direction: column; /* This ensures they stack */
  align-items: flex-start;
  gap: 5px; /* Space between the two legends */
  pointer-events: none; /* Allow clicks to pass through empty space */
}

.scalar-legend-group {
  margin-bottom: 5px;
}

.legend-separator {
  height: 1px;
  background-color: #ddd;
  margin: 1px 0;
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
  gap: 4px; /* Space between arrow tip and text */
  margin-top: 0px;
}

.vector-label {
  font-size: 0.75rem;
  color: #444;
  font-weight: 600;
  white-space: nowrap;
  margin-bottom: 1px;
}

/* Ensure the SVG handles overflow correctly */
.vector-arrow-svg {
  display: block; /* Removes weird inline spacing */
  overflow: visible;
}

.legend-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 3px 6px 3px 3px;
  border-radius: 6px;
  box-shadow: 0 0 8px rgba(0,0,0,0.2);
  width: 180px;
  pointer-events: auto; /* Re-enable clicks on the box itself */
  font-family: sans-serif;
  backdrop-filter: blur(2px);
}

.map-legend-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  margin-top: 5px;
  font-size: 0.75rem;
  color: #333;
  line-height: 1.2;
}

.map-legend-line {
  width: 20px;
  height: 3px;
  margin-right: 8px;
  border-radius: 1px;
}

.map-legend-label {
  font-size: 0.75rem;
  color: #333;
  font-weight: 600;       /* Semi-bold looks good here */
  white-space: nowrap;    /* Keeps text on one line */
}

@media (max-width: 600px) {
  /* On phones, move legend to top-right or squash it further */
  .legend-container {
    bottom: 25px; 
    left: 5px;
    gap: 5px;
  }

  .legend-box {
    width: 140px; /* Even smaller width */
    padding: 6px 8px;
  }
  
  .map-legend-item {
    font-size: 0.7rem; 
  }
  
  .vector-label {
    font-size: 0.65rem;
  }
  
  /* Hide the scalar gradient bar if it's too big, or make it smaller */
  .legend-bar {
    height: 12px;
  }
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
.map-legend h4,
.legend-box h4 {
  margin: 0px 0px 1px 2px !important;
  padding: 0 !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  color: #333;
  line-height: 1.1 !important;
  text-align: center;
}

/* BAR STYLING */
.legend-bar {
  height: 10px;
  width: 100%;
  border: 1px solid #ccc;
  margin-bottom: 1px;
}

.legend-bar-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 3px;
  font-size: 0.65rem;
  color: #666;
}


/* LEGEND GRADIENTS */
.viridis-gradient {
  background: linear-gradient(to right, #440154, #482878, #3e4989, #31688e, #26828e, #1f9e89, #35b779, #6ece58, #b5de2b, #fde725);
}
/* OLD BWR MAP .trend-gradient { background: linear-gradient(to right, #0000FF 0%, #4040FF 12.5%, #8080FF 25%, #BFBFFF 37.5%, #FFFFFF 50%, #FFBFBF 62.5%, #FF8080 75%, #FF4040 87.5%, #FF0000 100%); } */
.trend-gradient {
  background: linear-gradient(to right, #011261 0%, #024481 12.5%, #2E7CA6 25%, #92BDD2 37.5%, #EBEDEA 50%, #D4C096 62.5%, #AF8A3E 75%, #864C01 87.5%, #611200 100%);
}
.speed-gradient {
  background: linear-gradient(to right, 
    #FFFFFF 0.22%, #FFFFFF 14.9%, #FDFFFF 16.0%, #E4FFFE 20.5%, #D7FFFE 24.0%, #D7FFFE 45.4%,
    #D1FBFB 46.6%, #70BACE 50%, #308FB1 52.2%, #03719C 54.5%, #03719C 61.3%, #167798 62.4%, 
    #548B8A 64.7%, #939E7D 66.9%, #D1B26F 69.2%, #C75D0F 76.0%, #D42C01 80.5%, #E20000 85.0%, 
    #C50000 87.3%, #990000 90.7%, #6F0000 95.2%, #4C0100 99.7%
  );
}


/* --- FEEDBACK POPUP STYLES --- */
.feedback-popup {
  position: absolute;
  top: 50px; /* Adjust based on where your Layer Control sits */
  left: 70px;
  z-index: 9999; /* High z-index to sit above map tiles */
  background-color: white;
  padding: 12px 15px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  border-left: 4px solid #4CAF50; /* Nice green accent */
  max-width: 300px;
  font-family: 'Segoe UI', sans-serif;
  animation: slideIn 0.5s ease-out;
  cursor: default;
}

.feedback-content {
  font-size: 0.9rem;
  color: #333;
  line-height: 1.4;
}

.feedback-link {
  color: #2196F3;
  font-weight: 600;
  text-decoration: none;
}

.feedback-link:hover {
  text-decoration: underline;
}

.feedback-close {
  background: none;
  border: none;
  font-size: 1.5rem; /* Made slightly larger for visibility */
  color: #999;
  cursor: pointer;
  padding: 0 0 0 10px; /* added left padding for spacing */
  line-height: 0.8;    /* tighter line height centers the X better */
  font-family: Arial, sans-serif; /* Arial renders &times; reliably */
}

.feedback-close:hover {
  color: #333;
}


/* --- STATUS MESSAGE STYLES --- */
/* Container Position */
.status-toast {
  position: absolute;
  bottom: 30px;          /* Distance from bottom */
  left: 50%;
  transform: translateX(-50%); /* Center horizontally */
  z-index: 9999;         /* Ensure it's above the map */
  pointer-events: none;  /* Let clicks pass through to the map */
}

/* The Box Design */
.status-content {
  background: rgba(255, 255, 255, 0.9); /* Semi-transparent white */
  backdrop-filter: blur(4px);           /* Blur background behind it */
  padding: 10px 24px;
  border-radius: 50px;                  /* Pill shape */
  box-shadow: 0 4px 15px rgba(0,0,0,0.15);
  
  color: #333;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Optional: Simple CSS Spinner */
.message-display-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #ddd;
  border-top-color: #333; /* Dark spinner */
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Vue Transition Effects */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px); /* Slide up/down slightly */
}

/* Animations */
@keyframes slideIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Use 'deep' selector because these classes are inside Leaflet's SVG overlay */
:deep(.draggable-feature) {
  cursor: move;
  pointer-events: auto; /* Ensures the rectangle captures mouse clicks */
  transition: stroke-width 0.1s;
}

:deep(.draggable-feature:hover) {
  stroke-width: 2px; /* Thicken the line slightly when hovering */
  stroke-opacity: 0.8;
}

:deep(.draggable-feature:active) {
  cursor: grabbing;
}

</style>

<style>
/* LEAFLET OVERRIDES (Global Style)
   Force layer control to expand on hover instead of click 
*/
.leaflet-control-layers-base {
  display: none !important;
}
.leaflet-control-layers-separator {
  display: none !important;
}

.leaflet-control-layers {
  border: none !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
}

.leaflet-control-layers:hover {
  padding: 3px 6px 3px 3px !important;
  background: #fff !important;
  color: #333 !important;
  box-shadow: 0 1px 5px rgba(0,0,0,0.4) !important;
  border-radius: 5px !important;
  max-width: 200px;
}
.leaflet-control-layers:hover .leaflet-control-layers-list { display: block !important; font-size: 0.7rem; margin-bottom: 0; }
.leaflet-control-layers:hover .leaflet-control-layers-toggle { display: none !important; }

.leaflet-control-layers:hover label {
  margin-bottom: 1px !important; 
  margin-top: 1px !important;
  line-height: 0.9 !important;   
  display: flex !important;      
  align-items: center;           
  min-height: auto !important;   
}

/* Targets the actual checkbox/radio button to remove its default spacing */
.leaflet-control-layers:hover input {
  margin: 0 2px 0 0 !important; 
  height: 12px; 
  width: 12px;
}

@media (max-width: 480px) {
  .leaflet-control-layers {
    margin-top: 50px !important; 
    margin-right: 5px !important;
  }
}


</style>