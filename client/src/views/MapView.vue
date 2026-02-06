<template>
  <div class="page-container" :class="{ 'is-global-loading': isUploading || isFetching || isRefreshing }">
    
    <div class="map-wrapper" :class="{ 'show-labels': zoom >= 9 }" :style="{ height: mapHeightPercent + '%' }">
      <l-map 
        ref="map" 
        v-model:zoom="zoom" 
        v-model:center="center" 
        :use-global-leaflet="false" 
        @click="onMapClick"
		@mousemove="onMapMouseMove"  @mouseup="onMapMouseUp"
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
				
        <template v-for="(point, index) in selectedPoints" :key="point.id">
			<l-rectangle
			   :bounds="getSquareBounds( point.lat, point.lon, point.buffer !== undefined ? point.buffer : bufferSize )"
			   :color="point.color"
			   :fill-color="point.color"
			   :fill-opacity="0.3"
			   :weight="1"
			   :interactive="true" 
			   class-name="draggable-feature"
			   @mousedown="startPointDrag($event, point)"
			   @click="stopPropagation"  
			/>
			<l-circle-marker 
			   :lat-lng="[point.lat, point.lon]"
			   :radius="3" 
			   :color="point.color"
			   :fill-color="point.color"
			   :fill-opacity="1.0" 
			   :weight="1"
			   class-name="draggable-feature"
			   @mousedown="startPointDrag($event, point)"
			   @click="stopPropagation"
			>
			   <l-tooltip>{{ getSiteLabel(point, index) }}</l-tooltip>
			</l-circle-marker>
		</template>
		
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
                 <input type="checkbox" :value="v" v-model="pendingVars"> {{ v.toUpperCase() }}
               </label>
            </div>
          </div>

          <div class="opt-section">
            <span class="opt-label">Processing level:</span>
            <div class="opt-checks">
               <label v-for="q in availableQuality" :key="q">
                 <input type="checkbox" :value="q" v-model="pendingQuality"> {{ q }}
               </label>
            </div>
          </div>
		
		  <hr class="opt-divider">
          <div class="opt-section">
            <span class="opt-label">Smoothing Parameters:</span>
            
            <div class="param-row">
              <label>Max gap fill length days</label>
              <input type="range" v-model.number="pendingSmoothingParams.gap" min="1" max="120" class="param-slider">
              <input type="number" v-model.number="pendingSmoothingParams.gap" class="param-input">
            </div>

            <div class="param-row">
              <label>Window size days (Points)</label>
              <input type="range" v-model.number="pendingSmoothingParams.win_raw" min="1" max="121" step="2" class="param-slider">
              <input type="number" v-model.number="pendingSmoothingParams.win_raw" class="param-input">
            </div>

            <div class="param-row">
              <label>Window size days (Line)</label>
              <input type="range" v-model.number="pendingSmoothingParams.win_daily" min="1" max="121" step="2" class="param-slider">
              <input type="number" v-model.number="pendingSmoothingParams.win_daily" class="param-input">
            </div>

            <div class="param-row">
              <label>Polynomial order</label>
              <input type="range" v-model.number="pendingSmoothingParams.poly" min="1" max="5" class="param-slider">
              <input type="number" v-model.number="pendingSmoothingParams.poly" class="param-input">
            </div>
			
			<div class="action-row" style="margin-top: 15px; text-align: right;">
                <button class="btn-download" @click="applyAdvancedOptions" :disabled="isFetching">
                    <span v-if="isFetching" class="spinner"></span>
                    <span v-else>Update Timeseries</span>
                </button>
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
			<span v-if="!isUploading">Upload file</span>
			<span v-else class="spinner"></span>
			<input type="file" @change="handleFileUpload" accept=".zip,.geojson,.kml,.kmz" hidden :disabled="isUploading">
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
          <label>Buffer distance (m):</label>
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

        <p class="status-text"><span v-if="isFetching" class="spinner"></span> {{ statusMessage }}</p>
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
		
		<div class="custom-legend" v-if="legendItems.length > 0">
		
			<div class="legend-global-key">
			   <div class="key-item">
				  <span class="symbol-dot"></span><span>Points</span>
			   </div>
			   <div class="key-item">
				  <span class="symbol-line"></span><span>Daily</span>
			   </div>
			   <div class="key-item" v-if="showTrends">
				  <span class="symbol-dash"></span><span>Trend</span>
			   </div>
			</div>
			
			<div 
			   v-for="item in legendItems" 
			   :key="item.id" 
			   class="legend-item"
			   :class="{ 'is-hidden': !item.isVisible }"
			   @click="togglePointVisibility(item.id)"
			>
			   <span class="legend-label" :style="{ color: item.color }">
				  {{ item.label }}
			   </span>
			   
			   <span 
					  v-if="item.trendText" 
					  class="legend-trend" 
					  :style="{ color: item.color }"
					  v-html="item.trendText"
				></span>
			</div>
		</div>
		  
        <div id="velocity-chart" class="chart-container"></div>
	  
	    <div class="axis-controls" v-if="selectedPoints.length > 0">
		
		  <div class="axis-group">
			<label>Y-Min:</label>
			<input type="number" step="any" v-model.lazy="yAxisMin" @change="updatePlotAxes" />
			<label>Y-Max:</label>
			<input type="number" step="any" v-model.lazy="yAxisMax" @change="updatePlotAxes" />
		  </div>

		  <div class="axis-group">
			<label>Start:</label>
			<input type="text" placeholder="YYYY-MM-DD" v-model.lazy="xAxisMin" @change="updatePlotAxes" />
			<label>End:</label>
			<input type="text" placeholder="YYYY-MM-DD" v-model.lazy="xAxisMax" @change="updatePlotAxes" />
		  </div>
		  <button @click="resetAxes" class="btn-reset-axes">Reset</button>
		  
		  <div style="width: 1px; height: 20px; background: #ccc; margin: 0 5px;"></div>
		  <div class="trend-group">
			  <button 
				  @click="toggleTrends" 
				  class="btn-icon" 
				  :class="{ 'active': showTrends }"
				  title="Calculate Trend"
				>
				  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<line x1="2" y1="20" x2="22" y2="4" />
					<circle cx="6" cy="15" r="2" fill="currentColor" stroke="none" />
					<circle cx="12" cy="12" r="2" fill="currentColor" stroke="none" />
					<circle cx="18" cy="9" r="2" fill="currentColor" stroke="none" />
				  </svg>
				</button>

			  <div v-if="showTrends" style="display:flex; gap:5px; align-items:center;">
				  <label>Range:</label>
				  <input 
					 type="text" 
					 v-model.lazy="trendStart" 
					 @change="updateTrendCalc" 
					 placeholder="Start" 
					 class="trend-input"
				  />
				  <span>-</span>
				  <input 
					 type="text" 
					 v-model.lazy="trendEnd" 
					 @change="updateTrendCalc" 
					 placeholder="End" 
					 class="trend-input"
				  />
			  </div>
		  </div>
  
		</div>
		
    </div> 
	
  </div> 
  
  <div v-if="showHelp" class="modal-overlay" @click.self="showHelp = false">
      <div class="modal-content">
        <button class="modal-close" @click="showHelp = false">&times;</button>
        
        <h2>How to use SHIVER</h2>
        
        <div class="modal-body">
          <h3>1. Basic Usage</h3>
          <p>
            Click anywhere on the map or upload a shapefile containing a point or points to view 
			time-series of ice velocity in those locations. 
			After selecting a point, you can click-and-drag it to modify the position. 
			You can select up to ten points to compare different locations.
          </p>
		  <p>
            <strong>Buffer distance (m):</strong> When you click a location on the map, data are extracted from a small square centred 
			on your chosen point. The size of that square is controlled by the buffer distance text box. The default value is 500 m, which 
			produces a 1000 x 1000 m box (since we buffer outwards by 500 m from the chosen location). The value selected in this box
			applies to <strong>all</strong> your points. If you change the value in this box, it will refresh the data for all selected points.
			If you would prefer to have a different buffer distance for all points, then see Section 3: Uploading Files.
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
		  
          <h3>3. Uploading Files</h3>
          <p>
            <strong>Requirements:</strong>
          </p>
          <ul>
            <li><strong>Format:</strong> KMZ, KML, GeoJSON or a zipped shapefile (containing .shp, .shx, .dbf, and .prj files).</li>
            <li><strong>Projection:</strong> Must be in WGS84 (EPSG:4326) .</li>
            <li><strong>Type:</strong> Point or Multipoint geometries only. Maximum of ten points.</li>
          </ul>
		  <p>
            <strong>Optional:</strong>
          </p>
          <ul>
            <li><strong>Buffer:</strong> Include 'buffer' as a field name, containing integer buffer values in metres for each point.</li>
            <li><strong>Point names:</strong> Include 'name' as a field name to give your outputs a custom name.</li>
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
			When you click a point on the map an icon will appear showing the extraction location or region. 
			If you have used a buffer around your extraction location (recommended), the icon will be a square, 
			otherwise it will just be a point.
		  </p>
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
		   
		   
		  <h3>6. Interpreting the Chart</h3>
		  <p>
			The retrieved data are displayed as both points and a line. 
			Each point represents the average velocity in the selected location over a 6- or 12-day period centred on that time. 
			The corresponding error in that velocity estimate is displayed on the point as a vertical line (indicating the range of potential velocity estimates at that time). 
			The error is defined as the median velocity over bedrock regions at the time.
			A smoothed, daily velocity time-series is also plotted - this is linearly interpolated from the point data and then smoothed using a Savitzky-Golay filter. 
		  </p>
		  <p>
			You can optionally add a linear trend line to each of the selected time-series by clicking the 
			<svg style="width:1.2em;vertical-align:text-bottom" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="2" y1="20" x2="22" y2="4"/><g stroke="none" fill="currentColor"><circle cx="6" cy="15" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="18" cy="9" r="2"/></g></svg>
			button below the chart. This will add a dashed line to the chart and the retrieved trends and their 
			significance level will be displayed in the legend. 
			You can use the text boxes to adjust the time period over which the linear trend is calculated. 
			Four levels of trend significance may be displayed in the legend:
		  </p>
		  <ul>
            <li><strong>ns</strong> Not significant.</li>
			<li><strong>*</strong> Significant at the 0.05 level (i.e. p<0.05).</li>
			<li><strong>**</strong> Significant at the 0.01 level (i.e. p<0.01).</li>
			<li><strong>***</strong> Significant at the 0.001 level (i.e. p<0.001).</li>
		  </ul>
		  <p>
			Use the text boxes below the chart to adjust the x- and y-axis limits. 
			This will also change the .png image exports, however the .xslx will always contain the full time-series.
		  </p>
		  
		  <h3>7. Output</h3>
		  <p>
		    Clicking the map will produce a timeseries showing point data and a smoothed line. 
			The point data provide the measurements taken directly from our ice velocity dataset.
			The line provides a smoothed representation of those measurements.
		  </p>
          <p>
            Download your timeseries as <strong>.xlsx</strong> files and/or the graph(s) as a , 
            <strong>.png</strong> file. If multiple points are selected, the extracted timeseries will be 
			downloaded as a .zip file containing multiple .xslx files. If multiple variables 
			or filtering levels are selected, images will be downloaded as a .zip file.
			Downloads will also include a geojson of your point locations.
		  </p>
		  <p>
			<strong>Map downloads take a while! Be patient :-)</strong>
		  </p>
		  <p>
            <strong>XLSX naming convention:</strong> <br>
			SiteName_Buffer_Lat_Lon_SmoothingParams.xslx <br>
			e.g., Site_1_500m_67.123_-48.567_gf24_wr25_wd25_p2.xslx <br>
			where: gf24 means gap_fill=24 days, wr25 means raw window smoothing length of 25 days, wd25 means a daily window smoothing length of 25 days, and p2 means a second order polynomial in the savitzky-golay smoother was used.
		  </p>
		  <p>
			Each .xlsx file will contain three sheets:
		  </p>
		  <ul>
            <li><strong>Point Data:</strong> A timeseries of each velocity variable, velocity error, image pair time separation (days) and the number of finite values within the extraction area at each epoch. These form the points and whiskers plotted on the chart</li>
			<li><strong>Daily Data:</strong> A timeseries of each velocity variable interpolated to daily values. This forms the smooth line on the chart.</li>
			<li><strong>Metadata:</strong> A table containing the site details.</li>
		  </ul>
		  <p>
            <strong>Point data output variables:</strong>
			<br>
			<em>Note: Only "Date", "Error_m_yr", "Time_separation_days", "Pixel_Count" and "s_filt" are exported by default. 
			Other variables can be enabled for download within the Advanced Options menu. </em>
		  </p>
          <ul>
            <li><strong>Date:</strong> The central date of the two images used to estimate ice speed.</li>
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
		  <p>
            <strong>Daily data output variables:</strong>
			<br>
			<em>Note: Only "Date" and "s_filt" are exported by default. 
			Other variables can be enabled for download within the Advanced Options menu. </em>
		  </p>
          <ul>
            <li><strong>Date:</strong> The date of the interpolated velocity.</li>
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
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue';
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LCircleMarker, LGeoJson, LControlLayers, LLayerGroup, LControlScale, LRectangle, LTooltip } from "@vue-leaflet/vue-leaflet";
import axios from 'axios';
import Plotly from 'plotly.js-dist-min'; 
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import L from 'leaflet';
import html2canvas from 'html2canvas';
import domtoimage from 'dom-to-image-more';
import * as XLSX from 'xlsx';

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


// --- POINT DRAGGING FUNCTIONS --- //
// 1. Start Dragging (Attached to Rectangle AND Circle)
const startPointDrag = (e, point) => {
  // Prevent the click from bubbling to the map (prevents creating a new point)
  L.DomEvent.stopPropagation(e);
  L.DomEvent.preventDefault(e);

  // Disable map panning so the map stays still while we move the box
  if (map.value && map.value.leafletObject) {
    map.value.leafletObject.dragging.disable();
  }
  
  // Set the global cooldown flag immediately
  isDragCooldown.value = true;

  // Calculate the difference between the mouse cursor and the shape's center
  // This ensures the shape moves smoothly relative to where you grabbed it
  const mouseLat = e.latlng.lat;
  const mouseLng = e.latlng.lng;

  draggingState.value = {
    active: true,
    point: point, // Reference to the reactive point object
    offsetLat: point.lat - mouseLat,
    offsetLon: point.lon - mouseLng,
	startLat: point.lat,
    startLon: point.lon
  };
};

// 2. Move (Attached to the MAP)
const onMapMouseMove = (e) => {
  if (!draggingState.value.active) return;
  
  const state = draggingState.value;
  
  // Update the point's coordinates in real-time
  // Because 'state.point' is a reference to the item in 'selectedPoints',
  // Vue will automatically re-render the Rectangle and Circle at the new spot!
  state.point.lat = e.latlng.lat + state.offsetLat;
  state.point.lon = e.latlng.lng + state.offsetLon;
};

// 3. End Drag (Attached to the MAP)
const onMapMouseUp = async (e) => {
  if (!draggingState.value.active) return;

  // Re-enable map panning
  if (map.value && map.value.leafletObject) {
    map.value.leafletObject.dragging.enable();
  }
  
  // 1. Extract values BEFORE resetting the state
  const point = draggingState.value.point;
  const startLat = draggingState.value.startLat;
  const startLon = draggingState.value.startLon;

  // 2. Full State Reset (Cleaner)
  draggingState.value = { 
    active: false, 
    point: null, 
    offsetLat: 0, 
    offsetLon: 0,
    startLat: 0,
    startLon: 0
  };
  
  // Only fetch if the point moved significantly
  const hasMoved = Math.abs(point.lat - startLat) > 0.0001 || Math.abs(point.lon - startLon) > 0.0001;

  if (hasMoved) {
      await fetchSinglePoint(point.id, point.lat, point.lon, point.color);
  }

  // 2. Clear the cooldown flag after a short delay
  // This ensures the subsequent 'click' event (which happens ~10ms later) 
  // is still blocked by onMapClick
  setTimeout(() => {
      isDragCooldown.value = false;
  }, 100);
};

// 4. Stops clicks on the feature from bubbling up to the map
const stopPropagation = (e) => {
  // L.DomEvent.stopPropagation works on the native event wrapped inside the Leaflet event
  if (e.originalEvent) {
    L.DomEvent.stopPropagation(e.originalEvent);
  } else {
    L.DomEvent.stopPropagation(e);
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
const mapHeightPercent = ref(60); 
const isDragging = ref(false);
const isFlowActive = ref(false);
const globalMaskData = ref(null);
const globalOutlineData = ref(null);
const isFetching = ref(false);
const isRefreshing = ref(false);
const showTrends = ref(false);
const trendStart = ref(''); // YYYY-MM-DD
const trendEnd = ref('');   // YYYY-MM-DD
const legendItems = ref([]);
const isUserZoomed = ref(false);
const TIME_DELAY_MS = 90000; // 1.5 Minutes 
const STORAGE_KEY = 'shiver_feedback_shown';
const showFeedbackPopup = ref(false);
let timerInstance = null;

// Drag features
const isDragCooldown = ref(false);
const draggingState = ref({
  active: false,
  point: null,
  offsetLat: 0,
  offsetLon: 0,
  startLat: 0, 
  startLon: 0
});

// Chart
const xAxisMin = ref('');
const xAxisMax = ref('');
const yAxisMin = ref('');
const yAxisMax = ref('');

// --- ADVANCED OPTIONS ---
const showAdvanced = ref(false);
const availableVars = ['s', 'u', 'v'];
const availableQuality = ['filt', 'raw'];
const selectedVars = ref(['s']);         
const selectedQuality = ref(['filt']);   
const currentPlotVar = ref('s_filt');    

// Smoothing Parameters
const smoothingParams = ref({ gap: 24, win_raw: 1, win_daily: 25, poly: 2 });
const pendingVars = ref(['S']); 
const pendingQuality = ref(['filt']);
const pendingSmoothingParams = ref({ gap: 24, win_raw: 25, win_daily: 25, poly: 2 });

const restoreDefaults = () => {
  selectedVars.value = ['s'];
  selectedQuality.value = ['filt'];
  smoothingParams.value = { gap: 24, win_raw: 1, win_daily: 25, poly: 2 };
};

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

// Helper: Ensure the "Pending" state matches "Real" state when the component loads
onMounted(() => {
    // ... any existing onMounted code ...
    pendingVars.value = [...selectedVars.value];
    pendingQuality.value = [...selectedQuality.value];
    // Create a copy of the object to break reference
    pendingSmoothingParams.value = { ...smoothingParams.value };
});

const getSiteLabel = (point, index) => {
  // 1. Try Metadata Name (from Shapefile/Zarr) -> User Name -> Generic ID
  // Use optional chaining (?.) because point.data might be loading
  const meta = point.data?.meta || {};
  let name = meta.site_name || point.name || `Site_${point.id}`;
  // 2. If it is a generic name (e.g. Site_0, Site_99), force it to be sequential (Site_1, Site_2)
  if (/^Site_\d+$/.test(name)) {
    return `Site_${index + 1}`;
  }
  // 3. Otherwise return the custom name (e.g. "Jakobshavn")
  return name;
};

// --- FUNCTION 1: HANDLE CHART ZOOM (Chart updates Text Boxes) ---
const onPlotRelayout = (event) => {
  // 1. Check if this is an Auto-Range event (Double click or Reset)
  if (event['xaxis.autorange'] || event['yaxis.autorange']) {
      isUserZoomed.value = false; // UNLOCK
      // Clear variables logic (optional here as resetAxes handles it, but good for safety)
      if (event['xaxis.autorange']) { xAxisMin.value = ''; xAxisMax.value = ''; }
      if (event['yaxis.autorange']) { yAxisMin.value = ''; yAxisMax.value = ''; }
  } 
  // 2. Check if this is a Zoom event (User dragged box or axes)
  else if (event['xaxis.range[0]'] || event['yaxis.range[0]']) {
      isUserZoomed.value = true; // LOCK
      
      // Update X-Axis Variables
      if (event['xaxis.range[0]']) {
        xAxisMin.value = String(event['xaxis.range[0]']).split(' ')[0];
        xAxisMax.value = String(event['xaxis.range[1]']).split(' ')[0];
      }
      
      // Update Y-Axis Variables
      if (event['yaxis.range[0]']) {
        yAxisMin.value = Math.round(event['yaxis.range[0]'] * 100) / 100;
        yAxisMax.value = Math.round(event['yaxis.range[1]'] * 100) / 100;
      }
  }
};

// --- FUNCTION 2: HANDLE USER INPUT (Text Boxes update Chart) ---
const updatePlotAxes = () => {
  const graphDiv = document.getElementById('velocity-chart');
  if (!graphDiv) return;

  const update = {};
  isUserZoomed.value = true; // LOCK

  if (xAxisMin.value && xAxisMax.value) {
    update['xaxis.range'] = [xAxisMin.value, xAxisMax.value];
    update['xaxis.autorange'] = false;
  }

  if (yAxisMin.value !== '' && yAxisMax.value !== '') {
    update['yaxis.range'] = [parseFloat(yAxisMin.value), parseFloat(yAxisMax.value)];
    update['yaxis.autorange'] = false;
  }

  Plotly.relayout(graphDiv, update);
};

// --- FUNCTION 3: RESET BUTTON ---
const resetAxes = () => {
  const graphDiv = document.getElementById('velocity-chart');
  if (!graphDiv) return;

  isUserZoomed.value = false; // UNLOCK
  xAxisMin.value = ''; xAxisMax.value = '';
  yAxisMin.value = ''; yAxisMax.value = '';

  Plotly.relayout(graphDiv, {
    'xaxis.autorange': true,
    'yaxis.autorange': true
  });
};

// Function to calculate square bounds from a center point and buffer in meters
const getSquareBounds = (lat, lon, bufferMeters) => {
  // If buffer is 0, return the point itself (rectangle will be invisible)
  if (!bufferMeters || bufferMeters <= 0) return [[lat, lon], [lat, lon]];

  // Earth's radius approx calculation
  // 1 degree latitude is approx 111,111 meters
  const metersPerDegreeLat = 111111;
  
  // 1 degree longitude depends on latitude
  // Formula: 111,111 * cos(lat in radians)
  const metersPerDegreeLon = 111111 * Math.cos(lat * (Math.PI / 180));

  const deltaLat = bufferMeters / metersPerDegreeLat;
  const deltaLon = bufferMeters / metersPerDegreeLon;

  return [
    [lat - deltaLat, lon - deltaLon], // South-West corner
    [lat + deltaLat, lon + deltaLon]  // North-East corner
  ];
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
const downloadLabel = computed(() => selectedPoints.value.length > 1 ? 'All .xslx (.zip)' : '.xslx');
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

//  watch for changes to buffer size
watch(bufferSize, (newValue) => {
  if (newValue === "" || newValue === null || newValue === undefined) {
    bufferSize.value = 500; return;
  }
  debouncedRefetch();
});


const applyAdvancedOptions = async () => {
  // 1. VALIDATION: Ensure at least one variable and level is selected
  if (pendingVars.value.length === 0 || pendingQuality.value.length === 0) {
      alert("Warning: You must select at least one Variable and one Processing Level.");
      return; 
  }

  // 2. SMART CHECK: Do we need to fetch data?
  
  // Check if every NEW variable is present in the OLD list
  const isVarSubset = pendingVars.value.every(v => selectedVars.value.includes(v));
  
  // Check if every NEW level is present in the OLD list
  const isQualitySubset = pendingQuality.value.every(q => selectedQuality.value.includes(q));
  
  // Check if smoothing parameters changed (requires simple object comparison)
  const isParamsChanged = JSON.stringify(pendingSmoothingParams.value) !== JSON.stringify(smoothingParams.value);

  // We need to fetch if:
  // - We are ADDING a variable (not a subset)
  // - We are ADDING a quality level (not a subset)
  // - We changed smoothing parameters (affects values)
  const needsFetch = !isVarSubset || !isQualitySubset || isParamsChanged;

  // 3. COMMIT CHANGES (Update the "Real" variables)
  selectedVars.value = [...pendingVars.value];
  selectedQuality.value = [...pendingQuality.value];
  smoothingParams.value = { ...pendingSmoothingParams.value };

  // 4. EXECUTE
  if (needsFetch) {
      // User added data or changed params -> Trigger Backend
      await refetchAllPoints(); 
  } else {
      // User only removed data -> Just redraw the chart locally
      updateChart(); 
  }
};


// Refetch data for ALL points with the new buffer size and/or new filtering option
const refetchAllPoints = async () => {
  if (selectedPoints.value.length === 0) return;
  
  // 1. Setup State
  isRefreshing.value = true;
  const totalPoints = selectedPoints.value.length;
  
  const reqVars = selectedVars.value.length > 0 ? selectedVars.value : ['s'];
  const reqQual = selectedQuality.value.length > 0 ? selectedQuality.value : ['filt'];
  
  // Track refresh
  trackEvent("data_refresh", {
	  event_category: "interaction",
	  event_label: "data_refresh",
	  buffer: bufferSize.value,
	  variables: reqVars,
	  quality: reqQual,
	  region: currentRegion.value,
	});

  try {
    // 2. Iterate through points one by one
    for (let i = 0; i < totalPoints; i++) {
      const point = selectedPoints.value[i];
      
      // UPDATE STATUS: "Refreshing point 1 / 10..."
      statusMessage.value = `Refreshing point ${i + 1} / ${totalPoints}...`;

      // 3. Create Payload for THIS SPECIFIC POINT only
      const payload = {
        roi: [[point.lat, point.lon]], // Single ROI
        buffer: bufferSize.value,
        variables: reqVars, 
        quality: reqQual,
        gap_fill: smoothingParams.value.gap,
        win_raw: smoothingParams.value.win_raw,
        win_daily: smoothingParams.value.win_daily,
        poly: smoothingParams.value.poly
      };

      // 4. Fetch Data (Waits here until this point is done)
      const response = await apiClient.post('/api/timeseries/json', payload);
      
      // 5. Update the specific point in the array immediately
      // The backend returns an object like { "lat_lon": { data... } }
      // We grab the first (and only) value from the values array
      const newData = Object.values(response.data)[0];
      
      if (newData) {
        selectedPoints.value[i].data = newData;
      }
      
      // Optional: Update chart incrementally (cool visual effect)
      updateChart(); 
    }

    // 6. Finish
    updateChart(); 
    statusMessage.value = "Data updated.";

  } catch (error) {
    console.error("Failed to update:", error);
    statusMessage.value = "Error updating data.";
  } finally {
    isRefreshing.value = false;
  }
};

// --- MAP INTERACTION ---
const onMapClick = async (e) => {
// 1. Validation Checks 
  if (draggingState.value.active || isDragCooldown.value) return;
  const target = e.originalEvent?.target;
  if (!target || !target.isConnected) return;
  if (target.closest('.leaflet-control-container') || target.closest('.leaflet-control')) return;
  if (!map.value) return;
  
  if (selectedPoints.value.length >= 10) {
    alert("Maximum of 10 points allowed.");
    return;
  }
  
  // Ensure we don't fetch if the user has deselected everything in the menu
  if (pendingVars.value.length === 0 || pendingQuality.value.length === 0) {
      alert("Warning: Please select at least one Variable and Processing Level in Advanced Options.");
      return;
  }
  
  // Sync with advanced options
  // Commit the "Pending" menu state to the "Real" application state
  selectedVars.value = [...pendingVars.value];
  selectedQuality.value = [...pendingQuality.value];
  smoothingParams.value = { ...pendingSmoothingParams.value };
  
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
  
  // 1. VALIDATION: Ensure at least one variable/quality is selected (from Pending)
  if (pendingVars.value.length === 0 || pendingQuality.value.length === 0) {
      alert("Warning: Please select at least one Variable and Processing Level in Advanced Options before uploading.");
      event.target.value = ''; // Reset input
      return;
  }
  
  // 2. SYNC: Commit Pending Options to Real Options
  // This ensures the upload uses exactly what the user sees in the menu
  selectedVars.value = [...pendingVars.value];
  selectedQuality.value = [...pendingQuality.value];
  smoothingParams.value = { ...pendingSmoothingParams.value };
  
  // 3. Start loading state
  isUploading.value = true;
  statusMessage.value = "Uploading... 0%";
  
  const reqVars = selectedVars.value.length > 0 ? selectedVars.value : ['s'];
  const reqQual = selectedQuality.value.length > 0 ? selectedQuality.value : ['filt'];
  
  const formData = new FormData();
  formData.append("file", file);
  formData.append("buffer", bufferSize.value); // apply global buffer value in case shapefile does not specify it
  
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
	  const metaBuffer = data.meta?.buffer_used;
	  const hasSpecificBuffer = metaBuffer !== undefined && metaBuffer !== null;
	  const siteSpecificBuffer = hasSpecificBuffer ? Number(metaBuffer) : Number(bufferSize.value);
      const color = COLORS[selectedPoints.value.length % COLORS.length];
      // Extract
      selectedPoints.value.push({
        id: Date.now() + added, lat: ptLat, lon: ptLon, color: color, data: data, name: siteName, buffer: siteSpecificBuffer 
      });
      added++;
    }
	
    statusMessage.value = `Loaded ${added} sites.`;
    updateChart();
	
	// Clear input in case of additional uploads
	event.target.value = '';
	
  } catch (error) {
    console.error(error); 
	statusMessage.value = "Upload failed.";
	alert("Upload failed: " + (error.message || "Unknown error"));
  } finally {
    isUploading.value = false;
  }
};

// Fetch data for a single point (used by Map Click)
const fetchSinglePoint = async (id, lat, lon, color) => {
  isFetching.value = true;
  statusMessage.value = "Fetching...";
  const reqVars = selectedVars.value.length > 0 ? selectedVars.value : ['s'];
  const reqQual = selectedQuality.value.length > 0 ? selectedQuality.value : ['filt'];
  // Track data fetching
  trackEvent("data_fetch", {
	  event_category: "interaction",
	  event_label: "data_fetch",
	  buffer: bufferSize.value,
	  variables: reqVars,
	  quality: reqQual,
	  region: currentRegion.value,
	  lat: lat,
	  lon: lon
	});
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
  } finally {
    // 2. STOP SPINNER (Runs regardless of success or failure)
    isFetching.value = false;
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
  
  // Reset Legend Items
  legendItems.value = [];
  
  selectedPoints.value.forEach((point, idx) => {
    // Data validation
    if (point.data.status === 'error' || !point.data.data) return;
    const varData = point.data.data[plotKey];
    const rootData = point.data.data;
    if (!varData) return;
	
	// Setup styles
    const pale = makePale(point.color);
    const label = /^Site_\d+$/.test(point.name) ? `Site${idx+1}` : point.name;
    const suffix = plotKey.includes('raw') ? ' (Raw)' : '';
	
	// Check visibility (Default to true if undefined)
    const isVisible = point.visible !== false;
	
	// Select the correct error array based on the variable being plotted
	let activeErrorArray = rootData.error; // Default to Speed (Magnitude)
	if (plotKey.startsWith('u')) {
		 activeErrorArray = rootData.error_u || rootData.error; // Fallback if missing
	} else if (plotKey.startsWith('v')) {
		 activeErrorArray = rootData.error_v || rootData.error; // Fallback if missing
	}
	
	// --- PREPARE HOVER DATA ---
    // Zip count and dt together so each point has its specific metadata
    const customData = rootData.count.map((c, i) => [c, rootData.dt[i], activeErrorArray[i]]);
	
    // --- TRACE 1: MARKERS (Points) ---
    traces.push({
      x: rootData.dates, 
      y: varData.raw, 
      mode: 'markers', 
      type: 'scatter', 
      name: label, 
      showlegend: false, 
	  visible: isVisible,
      legendgroup: `g${point.id}`, 
      marker: { color: pale, size: 5, line: {width:1, color: point.color} },
      error_y: { type: 'data', array: activeErrorArray, visible: true, color: pale, thickness: 1, width: 0 },
      error_x: { type: 'data', array: rootData.dt?.map(d=>d/2), visible: true, color: pale, thickness: 1, width: 0 },
	  customdata: customData,
      hovertemplate: 
        `<b>Date</b>: %{x|%Y-%m-%d}<br>` +
        `<b>Value</b>: %{y:.1f} &plusmn; %{customdata[2]:.1f} m/yr<br>` + 
        `<b>Pixels</b>: %{customdata[0]}<br>` +
        `<b>dt</b>: %{customdata[1]} days` +
        `<extra></extra>`
    });
    
    // --- TRACE 2: LINES (Smoothed) ---
    traces.push({
      x: rootData.dates, 
      y: varData.smoothed, 
      mode: 'lines', 
      type: 'scatter', 
      name: label,
      showlegend: false,
	  visible: isVisible,
      legendgroup: `g${point.id}`, 
      line: { color: point.color, width: 3 }
    });
	
	// TREND LINE LOGIC
	let trendText = null;
    if (showTrends.value && trendStart.value && trendEnd.value) {
        
        // 1. Filter Data to the selected Trend Range
        const tStart = new Date(trendStart.value).getTime();
        const tEnd = new Date(trendEnd.value).getTime();
        const filteredDates = [];
        const filteredVals = [];
        rootData.dates.forEach((d, i) => {
            const t = new Date(d).getTime();
            const val = varData.raw[i]; 
            if (t >= tStart && t <= tEnd && val !== null && val !== undefined) {
                filteredDates.push(d);
                filteredVals.push(val);
            }
        });

        // 2. Calculate Regression
        const stats = calculateRegression(filteredDates, filteredVals);

        if (stats) {
			const x1 = tStart;
			const x2 = tEnd;
			const y1 = stats.slope * x1 + stats.intercept;
			const y2 = stats.slope * x2 + stats.intercept;
			
			// Format trend values
			const trendVal = stats.slopePerYear > 0 
			   ? `+${stats.slopePerYear.toFixed(1)}` 
			   : stats.slopePerYear.toFixed(1);

			let sig = '';
			if (stats.pValue < 0.001) sig = '***';
			else if (stats.pValue < 0.01) sig = '**';
			else if (stats.pValue < 0.05) sig = '*';
			else sig = 'ns'; // not significant
			
			// Define trend text
            trendText = `${trendVal} m/yr<sup>2</sup> (${sig})`;

			// Define trend data
			traces.push({
				x: [trendStart.value, trendEnd.value],
				y: [y1, y2],
				mode: 'lines',
				type: 'scatter',
				legendgroup: `g${point.id}`,
				showlegend: false,
				visible: isVisible,
				line: { color: point.color, width: 2, dash: 'dash' },
				hoverinfo: 'skip' 
			});
		}
    }
	
	// --- POPULATE CUSTOM LEGEND ---
    // Instead of a dummy trace, we push to our Vue array
    legendItems.value.push({
        id: point.id,
        label: `${label}${suffix}`,
        color: point.color,
        trendText: trendText,
        isVisible: isVisible
    });
	
  });
  
  // Define axis labels
  let yAxisLabel = "Velocity (m/yr)";
  if (plotKey.startsWith('s')) yAxisLabel = "Speed (m/yr)";
  else if (plotKey.startsWith('u')) yAxisLabel = "Easting velocity (m/yr)";
  else if (plotKey.startsWith('v')) yAxisLabel = "Northing velocity (m/yr)";

  const layout = {
	annotations: [
      {
        text: "S H I V E R",
        x: 0.5, // Horizontal center
        y: 0.5, // Vertical center
        xref: "paper", // Position relative to the chart area (0-1)
        yref: "paper",
        showarrow: false,
        font: {
          family: "sans-serif",
          size: 200, // Large font
          color: "rgba(135, 206, 235, 0.15)", // Faint Sky Blue (low opacity)
          weight: 600
        },
        textangle: 0, // Optional: slight rotation for style
        layer: "below"  // Tries to put it behind data (though Plotly text often sits on top)
      }
    ],
    title: `Ice Velocity: ${plotKey.toUpperCase()}`,
    xaxis: { title: { text: 'Date', standoff: 15 }, showline: true, linewidth: 1, linecolor: 'black', mirror: true, automargin: true },
    yaxis: { title: { text: yAxisLabel, standoff: 15 }, showline: true, linewidth: 1, linecolor: 'black', mirror: true, automargin: true },
    margin: {t:5, r:20, l:60, b:40}, 
    showlegend: false, 
    autosize: true
  };

  return { data: traces, layout };
};

// --- NEW HANDLER: Toggle Visibility ---
const togglePointVisibility = (id) => {
    const point = selectedPoints.value.find(p => p.id === id);
    if (point) {
        // Toggle property
        point.visible = point.visible === false ? true : false;
        // Trigger chart update
        updateChart();
    }
};

// PLOT CHART
const updateChart = async () => {
  await nextTick(); 
  if (selectedPoints.value.length === 0) { 
      Plotly.purge('velocity-chart'); 
      legendItems.value = []; 
      xAxisMin.value = ''; xAxisMax.value = '';
      yAxisMin.value = ''; yAxisMax.value = '';
      isUserZoomed.value = false;
      return; 
  }
  
  const { data, layout } = buildChartConfig(currentPlotVar.value);
  
  // Zoom if user interacted
  if (isUserZoomed.value) {
      if (xAxisMin.value && xAxisMax.value) {
         layout.xaxis.range = [xAxisMin.value, xAxisMax.value];
         layout.xaxis.autorange = false;
      }
      
      if (yAxisMin.value !== '' && yAxisMax.value !== '') {
         layout.yaxis.range = [parseFloat(yAxisMin.value), parseFloat(yAxisMax.value)];
         layout.yaxis.autorange = false;
      }
  }
  
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
  const graphDiv = await Plotly.newPlot('velocity-chart', data, layout, config);
  
  //Attach listener for axis updates
  if (graphDiv) {
    graphDiv.removeAllListeners && graphDiv.removeAllListeners('plotly_relayout');
    graphDiv.on('plotly_relayout', onPlotRelayout);
    
    // 3. POPULATE INITIAL VALUES (New Code)
    // We read the calculated range from the chart's internal layout
    if (graphDiv.layout && graphDiv.layout.xaxis && graphDiv.layout.yaxis) {
        const xRange = graphDiv.layout.xaxis.range;
        const yRange = graphDiv.layout.yaxis.range;

        if (xRange) {
            xAxisMin.value = String(xRange[0]).split(' ')[0];
            xAxisMax.value = String(xRange[1]).split(' ')[0];
        }
        if (yRange) {
            yAxisMin.value = Math.round(yRange[0] * 100) / 100;
            yAxisMax.value = Math.round(yRange[1] * 100) / 100;
        }
    }
	// Force resize
	window.requestAnimationFrame(() => {
        Plotly.Plots.resize(graphDiv);
    });
  }
};


const calculateRegression = (xDates, yValues) => {
  const n = xDates.length;
  if (n < 2) return null;

  // 1. Constants
  const MS_PER_YEAR = 1000 * 60 * 60 * 24 * 365.25;

  const x = xDates.map(d => new Date(d).getTime());
  const y = yValues;

  let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0, sumYY = 0;
  for (let i = 0; i < n; i++) {
    sumX += x[i];
    sumY += y[i];
    sumXY += x[i] * y[i];
    sumXX += x[i] * x[i];
    sumYY += y[i] * y[i];
  }

  // 2. Calculate Raw Slope (Change per Millisecond)
  const rawSlope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
  const intercept = (sumY - rawSlope * sumX) / n;

  // 3. Convert to "Change per Year"
  const slopePerYear = rawSlope * MS_PER_YEAR;

  // 4. Stats (R2 and P)
  const ssTot = sumYY - (sumY * sumY) / n;
  const ssRes = sumYY - rawSlope * sumXY - intercept * sumY;
  const r2 = 1 - (ssRes / ssTot);

  const s2 = ssRes / (n - 2); 
  const seSlope = Math.sqrt(s2 / (sumXX - (sumX * sumX) / n));
  const tStat = rawSlope / seSlope;
  const pValue = getPValueFromT(Math.abs(tStat), n - 2);

  // Return both raw (for plotting) and converted (for display)
  return { slope: rawSlope, intercept, slopePerYear, r2, pValue };
};

// --- HANDLER: Toggle Trends ---
const toggleTrends = async () => {
  showTrends.value = !showTrends.value;

  if (showTrends.value) {
    // 1. Default the Trend Range to the CURRENT visible chart range
    // If user has zoomed, use that. If not, use global bounds.
    if (xAxisMin.value && xAxisMax.value) {
      trendStart.value = xAxisMin.value;
      trendEnd.value = xAxisMax.value;
    } else {
      // Fallback: Use the very first and last date of the data
      // (Simplified logic: grab from first point)
      if (selectedPoints.value.length > 0) {
        const dates = selectedPoints.value[0].data.data.dates;
        trendStart.value = dates[0];
        trendEnd.value = dates[dates.length - 1];
      }
    }
  }

  // 2. Refresh Chart
  await updateChart();
};

// --- HANDLER: Update when Trend Dates change ---
const updateTrendCalc = async () => {
   if (showTrends.value) {
     await updateChart();
   }
};

// Approximate two-tailed p-value from t-stat (Abramowitz & Stegun approx)
const getPValueFromT = (t, df) => {
  const x = df / (df + t * t);
  let p = 0; 
  // Beta function approximation loop
  // (Simplified for brevity: returns rough significance tiers if math is too heavy)
  // For a robust implementation without libraries, simple thresholds are often used in UI:
  if (Math.abs(t) > 3.291) return 0.001; // roughly p < 0.001
  if (Math.abs(t) > 2.576) return 0.01;  // roughly p < 0.01
  if (Math.abs(t) > 1.960) return 0.05;  // roughly p < 0.05
  return 0.10; // Not significant
};

const setWaitCursor = (shouldWait) => {
  if (shouldWait) {
    const style = document.createElement('style');
    style.id = 'global-wait-cursor';
    style.innerHTML = '* { cursor: wait !important; }'; // The "Nuclear" override
    document.head.appendChild(style);
  } else {
    const style = document.getElementById('global-wait-cursor');
    if (style) style.remove();
  }
};


// CHART IMAGE DOWNLOAD (MULTI-FILE SUPPORT) ---
const downloadChartImage = async () => {
  if (selectedPoints.value.length === 0) return;

  statusMessage.value = "Processing charts...";
  
  // 1. Force Cursor (Nuclear Option)
  setWaitCursor(true);
  
  const EXPORT_SCALE = 3; 
  const originalPlotVar = currentPlotVar.value;

  // 2. Use setTimeout to allow the UI to paint the cursor change
  setTimeout(async () => {
    try {
      const zip = new JSZip();
      const optionsProcess = plotOptions.value.length > 0 ? plotOptions.value : [{val: currentPlotVar.value, label: 'Current'}];
      const filesToSave = [];

      for (const opt of optionsProcess) {
        statusMessage.value = `Capturing ${opt.label || opt.val}...`;

        // Update View
        if (currentPlotVar.value !== opt.val) {
            currentPlotVar.value = opt.val;
            await nextTick();
            // Give Plotly time to settle
            await new Promise(r => setTimeout(r, 800)); 
        }

        const chartElement = document.querySelector('.chart-wrapper');
        const width = chartElement.clientWidth;
        const height = chartElement.clientHeight;

        const imgUrl = await domtoimage.toPng(chartElement, {
            bgcolor: '#FFFFFF', 
            width: width * EXPORT_SCALE,
            height: height * EXPORT_SCALE,
            style: {
              transform: `scale(${EXPORT_SCALE})`,
              transformOrigin: 'top left',
              width: `${width}px`,
              height: `${height}px`
            },
            // Filter out UI elements (Toolbar & Text Inputs)
            filter: (node) => {
                if (node.classList) {
                    if (node.classList.contains('modebar')) return false;
                    if (node.classList.contains('axis-controls')) return false; 
                    if (node.tagName === 'INPUT' || node.tagName === 'SELECT') return false;
                }
                return true;
            }
        });

        const blob = await (await fetch(imgUrl)).blob();
        const fname = `velocity_${opt.val}_timeseries${smoothingSuffix.value}.png`;
        filesToSave.push({ name: fname, blob: blob });
      }

      // Restore State
      if (currentPlotVar.value !== originalPlotVar) {
          currentPlotVar.value = originalPlotVar;
      }

      // Save & Track
      if (filesToSave.length === 1) {
        saveAs(filesToSave[0].blob, filesToSave[0].name);
        statusMessage.value = "Chart downloaded.";
        trackEvent("file_download", {
             event_category: "export",
             event_label: "png_chart",
             file_extension: "png",
             file_name: filesToSave[0].name,
             plot_type: currentPlotVar.value
        });
      } else {
        filesToSave.forEach(f => zip.file(f.name, f.blob));
        statusMessage.value = "Compressing...";
        const content = await zip.generateAsync({type:"blob"});
        saveAs(content, `Velocity_Charts_${currentRegion.value}.zip`);
        statusMessage.value = "All charts downloaded.";
        trackEvent("file_download", {
             event_category: "export",
             event_label: "png_chart",
             file_extension: "png",
             file_name: "zipped_charts",
             plot_type: currentPlotVar.value
        });
      }

    } catch (error) {
      console.error("Chart Export Error:", error);
      statusMessage.value = "Error generating chart.";
    } finally {
      // 3. Remove Nuclear Cursor
      setWaitCursor(false);
      // Optional: clear status message after a moment
      setTimeout(() => statusMessage.value = "", 2000);
    }
  }, 100); // 100ms delay to ensure browser paints the cursor
};



const downloadMapAndGraph = async () => {
  if (selectedPoints.value.length === 0) return;

  isDownloadingMap.value = true;
  statusMessage.value = "Processing images...";
  
  // 1. Force "Nuclear" Wait Cursor
  setWaitCursor(true);

  // SETTINGS
  const EXPORT_SCALE = 3; 
  
  // Store original selection to restore later
  const originalPlotVar = currentPlotVar.value;

  setTimeout(async () => {
    try {
      // --- 1. Capture the Map (Once) ---
      const mapElement = document.querySelector('.map-wrapper');
      const mapWidth = mapElement.clientWidth;
      const mapHeight = mapElement.clientHeight;

      const mapImgUrl = await domtoimage.toPng(mapElement, {
          width: mapWidth * EXPORT_SCALE,
          height: mapHeight * EXPORT_SCALE,
          style: {
            transform: `scale(${EXPORT_SCALE})`,
            transformOrigin: 'top left',
            width: `${mapWidth}px`,
            height: `${mapHeight}px`
          },
          // Filter out Map Controls
          filter: (node) => {
            if (node.classList) {
                if (node.classList.contains('control-panel')) return false;
                if (node.classList.contains('leaflet-control-zoom')) return false;
                if (node.classList.contains('leaflet-control-layers')) return false;
                if (node.classList.contains('feedback-popup')) return false;
            }
            return true;
          }
      });

      const mapImg = new Image();
      mapImg.src = mapImgUrl;
      await new Promise(resolve => mapImg.onload = resolve);

      // --- 2. Loop Through Variables ---
      const zip = new JSZip();
      const optionsProcess = plotOptions.value.length > 0 ? plotOptions.value : [{val: currentPlotVar.value, label: 'Current'}];
      const filesToSave = [];

      for (const opt of optionsProcess) {
        statusMessage.value = `Capturing ${opt.label || opt.val}...`;

        // A. Update the Chart View
        if (currentPlotVar.value !== opt.val) {
            currentPlotVar.value = opt.val;
            await nextTick(); 
            await new Promise(r => setTimeout(r, 800)); 
        }

        // B. Capture the Chart (Screenshot)
        const chartElement = document.querySelector('.chart-wrapper');
        const chartWidth = chartElement.clientWidth;
        const chartHeight = chartElement.clientHeight;

        const chartImgUrl = await domtoimage.toPng(chartElement, {
            bgcolor: '#FFFFFF', 
            width: chartWidth * EXPORT_SCALE,
            height: chartHeight * EXPORT_SCALE,
            style: {
              transform: `scale(${EXPORT_SCALE})`,
              transformOrigin: 'top left',
              width: `${chartWidth}px`,
              height: `${chartHeight}px`
            },
            // === NEW: Filter out Chart Controls/Inputs ===
            filter: (node) => {
                if (node.classList) {
                    if (node.classList.contains('modebar')) return false; // Plotly Toolbar
                    if (node.classList.contains('axis-controls')) return false; // Container for inputs (if class exists)
                    // Generic catch-all for Inputs and Dropdowns
                    if (node.tagName === 'INPUT' || node.tagName === 'SELECT') return false;
                }
                return true;
            }
        });

        const chartImg = new Image();
        chartImg.src = chartImgUrl;
        await new Promise(resolve => chartImg.onload = resolve);

        // C. Stitch Map + Chart
        const combinedCanvas = document.createElement('canvas');
        const ctx = combinedCanvas.getContext('2d');
        
        const finalWidth = mapImg.naturalWidth;
        const chartAspectRatio = chartImg.naturalWidth / chartImg.naturalHeight;
        const finalChartHeight = finalWidth / chartAspectRatio;
        const finalHeight = mapImg.naturalHeight + finalChartHeight;

        combinedCanvas.width = finalWidth;
        combinedCanvas.height = finalHeight;

        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(0, 0, finalWidth, finalHeight);
        
        ctx.drawImage(mapImg, 0, 0);
        ctx.drawImage(chartImg, 0, mapImg.naturalHeight, finalWidth, finalChartHeight);

        const blob = await new Promise(resolve => combinedCanvas.toBlob(resolve, 'image/png'));
        
        // D. Create Filename
        const fname = `velocity_${opt.val}_timeseries${smoothingSuffix.value}_map.png`;
        filesToSave.push({ name: fname, blob: blob });
      }

      // Restore original view state
      if (currentPlotVar.value !== originalPlotVar) {
          currentPlotVar.value = originalPlotVar;
      }

      // --- 3. Save & Track ---
      if (filesToSave.length === 1) {
        saveAs(filesToSave[0].blob, filesToSave[0].name);
        statusMessage.value = "Image downloaded.";
        
        trackEvent("file_download", {
            event_category: "export",
            event_label: "png_map",
            file_extension: "png",
            file_name: filesToSave[0].name,
            plot_type: currentPlotVar.value
        });
      } else {
        filesToSave.forEach(f => zip.file(f.name, f.blob));
        statusMessage.value = "Compressing...";
        const content = await zip.generateAsync({type:"blob"});
        saveAs(content, `Map_Velocity_Export_${currentRegion.value}.zip`);
        statusMessage.value = "All charts downloaded.";
        
        trackEvent("file_download", {
            event_category: "export",
            event_label: "png_map",
            file_extension: "png",
            file_name: "zipped_maps",
            plot_type: currentPlotVar.value
        });
      }

    } catch (error) {
      console.error("Map Export Error:", error);
      statusMessage.value = "Error generating images.";
    } finally {
      isDownloadingMap.value = false;
      // 2. Remove "Nuclear" Cursor
      setWaitCursor(false);
      setTimeout(() => statusMessage.value = "", 2000);
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
  return `${name}_${buf}m_${lat}_${lon}${smoothingSuffix.value}.xlsx`;
};

// --- DATA DOWNLOAD HANDLER ---
const handleDownload = async () => {
  if (selectedPoints.value.length === 0) return;
  
  // Track downloads (Metadata updated to reflect xlsx)
  trackEvent("file_download", {
      event_category: "export",
      event_label: "xlsx_data", 
      file_extension: selectedPoints.value.length === 1 ? "xlsx" : "zip", 
      file_name: selectedPoints.value.length === 1 ? getFilename(selectedPoints.value[0], 0) : "velocity_data_batch",
      region: currentRegion.value,
      count: selectedPoints.value.length
  });
  
  // --- SINGLE FILE DOWNLOAD ---
  if (selectedPoints.value.length === 1) {
    const p = selectedPoints.value[0];
    // Pass index 0 since it's a single file
    const wb = generateXLSX(p, 0);
    XLSX.writeFile(wb, getFilename(p, 0)); 
    return;
  }

  // --- BATCH DOWNLOAD (ZIP) ---
  isDownloading.value = true;
  try {
    const zip = new JSZip();
    
    // 1. Add XLSX Files to Zip
    selectedPoints.value.forEach((p, index) => {
      const wb = generateXLSX(p, index);
      // Generate binary buffer for the zip
      const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      zip.file(getFilename(p, index), wbout);
    });

    // 2. Add GeoJSON Summary (Unchanged logic)
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

const generateXLSX = (point, index) => {
  const rootData = point.data.data; 
  const wb = XLSX.utils.book_new();
  
  if (!rootData) return wb;

  // 1. IDENTIFY VARIABLES
  // Find all velocity keys (s_filt, u_raw, etc), excluding meta keys
  const availableKeys = Object.keys(rootData).filter(k => !['dates', 'dates_daily', 'error', 'error_u', 'error_v', 'dt', 'count'].includes(k));

  // ==========================================
  // SHEET 1: POINT DATA (Skips NaNs)
  // ==========================================
  const pointRows = [];
  
  // Create Headers
  const pointHeaders = ["Date", "Error_m_yr","Error_U_m_yr","Error_V_m_yr", "Time_Separation_days", "Pixel_Count", ...availableKeys];
  pointRows.push(pointHeaders);

  rootData.dates.forEach((date, i) => {
     // Check for NaN in the first available variable (usually 's')
     if (availableKeys.length > 0) {
        const firstKey = availableKeys[0];
        // Note: Check both .raw (if exists) or direct value depending on your data structure
        // Assuming your structure is rootData[key].raw[i] based on your previous code:
        const checkVal = rootData[firstKey]?.raw ? rootData[firstKey].raw[i] : rootData[firstKey][i];
        
        if (checkVal === null || checkVal === undefined || Number.isNaN(checkVal)) { return; } // SKIP ROW
     }

     const errorMag = rootData.error ? rootData.error[i] : '';
	 const errorU = rootData.error_u ? rootData.error_u[i] : '';
     const errorV = rootData.error_v ? rootData.error_v[i] : '';
     const dt = rootData.dt ? rootData.dt[i] : '';
     const count = rootData.count ? rootData.count[i] : 0;

     const row = [date, errorMag, errorU, errorV, dt, count];
     availableKeys.forEach(k => {
         const val = rootData[k]?.raw ? rootData[k].raw[i] : rootData[k][i];
         row.push(val !== null ? val : '');
     });
     pointRows.push(row);
  });

  const wsPoint = XLSX.utils.aoa_to_sheet(pointRows);
  XLSX.utils.book_append_sheet(wb, wsPoint, "Point Data");

  // ==========================================
  // SHEET 2: DAILY DATA (Keeps NaNs)
  // ==========================================
  // Assuming 'dates_daily' exists in your data structure. 
  // If not, fallback to 'dates' or an empty array.
  const dailyDates = rootData.dates_daily || rootData.dates; 
  
  if (dailyDates && dailyDates.length > 0) {
      const dailyRows = [];
      const dailyHeaders = ["Date", ...availableKeys];
      dailyRows.push(dailyHeaders);

      dailyDates.forEach((date, i) => {
          const row = [date];
          availableKeys.forEach(k => {
              // Assuming daily data is stored in .daily[i]
              // Adjust this path if your data structure is different!
              // e.g., rootData.s.daily[i]
              const val = rootData[k]?.smoothed ? rootData[k].smoothed[i] : null;
              row.push(val !== null && val !== undefined ? val : ''); 
          });
          dailyRows.push(row);
      });

      const wsDaily = XLSX.utils.aoa_to_sheet(dailyRows);
      XLSX.utils.book_append_sheet(wb, wsDaily, "Daily Data");
  }

  // ==========================================
  // SHEET 3: METADATA
  // ==========================================
  const meta = point.data.meta || {};
  let siteName = meta.site_name || point.name || `Site_${point.id}`;
  if (/^Site_\d+$/.test(siteName)) { siteName = `Site_${index + 1}`; }
  const metaRows = [
      ["Property", "Value"], // Header
      ["Site Name", siteName],
      ["Latitude", point.lat],
      ["Longitude", point.lon],
      ["Buffer (m)", meta.buffer_used || bufferSize.value],
      ["Region", currentRegion.value],
      ["Smoothing Suffix", smoothingSuffix.value],
      ["Export Date", new Date().toISOString()]
  ];


  const wsMeta = XLSX.utils.aoa_to_sheet(metaRows);
  XLSX.utils.book_append_sheet(wb, wsMeta, "Metadata");

  return wb;
};


</script>

<style scoped>
/* --- MAIN LAYOUT --- */
.page-container { display: flex; flex-direction: column; height: calc(100vh - 60px); width: 100%; overflow: hidden; }
.map-wrapper { position: relative; width: 100%; user-select: none; }
.chart-wrapper { width: 100%; background: white; position: relative; overflow: hidden; display: flex; flex-direction: column;}
.chart-container { width: 100%; flex: 1; min-height: 0;}
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
  margin-right: 8px;
  position: relative;
  top: -1px;
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


/* --- CHART --- */
.axis-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 8px;
  background: #f8f9fa;
  border-top: 1px solid #ddd;
  font-size: 0.85rem;
  position: relative; 
  z-index: 10;
  flex-shrink: 0; 
}

.axis-group {
  display: flex;
  align-items: center;
  gap: 5px;
}

.axis-group label {
  font-weight: 600;
  color: #555;
  margin-right: 2px;
}

.axis-group input {
  width: 70px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
  font-size: 0.85rem;
}

.btn-reset-axes {
  background: white;
  border: 1px solid #aaa;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  color: #333;
}

.btn-reset-axes:hover {
  background: #eee;
  color: #d9534f;
  border-color: #d9534f;
}

.btn-icon {
  background: white;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  color: #555;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f0f0f0;
  color: #000;
}

.btn-icon.active {
  background: #e6f7ff; 
  color: #1890ff;    
  border-color: #1890ff;
}

.trend-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trend-input {
  width: 85px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  text-align: center;
  font-size: 0.85rem;
  background-color: #fffbe6; 
}

/* CUSTOM LEGEND STYLES */
.custom-legend {
  display: flex;
  flex-wrap: wrap; 
  gap: 15px;       
  padding: 4px 10px 4px 65px;
  background: #fff;
  border-bottom: 1px solid #eee;
  min-height: 0px;
  justify-content: flex-start; 
  align-items: flex-start;
  position: relative;
  z-index: 20;
}

.legend-item {
  cursor: pointer;
  font-size: 0.85rem;
  user-select: none;
  display: flex;
  flex-direction: column; 
  align-items: flex-start;
  line-height: 1.2;
  gap: 0;
  transition: opacity 0.2s;
}

.legend-item:hover {
  opacity: 0.8;
}

/* Dim hidden items */
.legend-item.is-hidden {
  opacity: 0.4;
  text-decoration: line-through; 
}

.legend-label {
  font-weight: 700; 
}

.legend-trend {
  font-weight: 400; /* Normal weight for stats */
  font-size: 0.8em; /* Slightly smaller */
  margin-top: -1px;
}

.legend-global-key {
  position: absolute;
  top: 100%; 
  left: 65px; 
  margin-top: 10px; 
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 15px;
  color: #555;
  font-size: 0.8rem;
  font-weight: 600;
  background: rgba(255,255,255,0.8); padding: 2px 5px; border-radius: 4px; 
  pointer-events: none; 
  z-index: 20;
}

.key-item {
  display: flex;
  align-items: center;
  gap: 6px; /* Space between the Symbol and the Word */
}

.key-separator {
  width: 1px;
  height: 20px;
  background: #ddd;
  margin-left: 5px;
}

.symbol-dot, .symbol-line, .symbol-dash {
  display: block;    
  flex-shrink: 0;    
}

.symbol-dot {
  width: 6px;
  height: 6px;
  background-color: #777;
  border-radius: 50%;
  border: 1px solid #777; /* Mimic the chart point style */
}

.symbol-line {
  width: 14px;
  height: 3px;
  background-color: #777;
  border-radius: 1px;
}

.symbol-dash {
  width: 14px;
  height: 0;
  border-top: 2px dashed #777;
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