<template>
  <div class="page-container" :class="{ 'is-global-loading': isUploading || isFetching || isRefreshing }">
    
    <div class="map-wrapper" :class="{ 'show-labels': zoom >= 9 }" :style="{ height: mapHeightPercent + '%' }">
      <l-map 
        ref="map" 
        v-model:zoom="zoom" 
        v-model:center="center" 
        :use-global-leaflet="false" 
		:options="{ zoomControl: false }"
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
		  crossOrigin="anonymous"
        ></l-tile-layer>
		
		<div class="map-title-overlay">
		  <h1 class="shiver-title">SHIVER</h1>
		  <div class="shiver-subtitle">SHeffield Ice Velocity ExploreR</div>
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
			   :bounds="getSquareBounds( point.lat, point.lon, point.buffer !== undefined ? point.buffer : pendingBuffer.value )"
			   :color="point.color"
			   :fill-color="point.color"
			   :fill-opacity="0.3"
			   :weight="1"
			   :interactive="true" 
			   class-name="draggable-feature"
			   @mousedown="startPointDrag($event, index)"
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
			   @mousedown="startPointDrag($event, index)"
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
				  <div class="legend-bar-labels">
					<span>1</span>
					<span>10</span>
					<span>100</span>
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
				  title="Upload File"
				>
				  <input type="file" @change="handleFileUpload" accept=".zip,.geojson,.kml,.kmz" hidden :disabled="isUploading">
				  <span v-if="isUploading" class="spinner-small"></span>
				  <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="17 8 12 3 7 8" />
					<line x1="12" y1="3" x2="12" y2="15" />
				  </svg>
				</label>

				<button 
				  class="panel-btn" 
				  @click="showAdvanced = !showAdvanced" 
				  :class="{ 'active': showAdvanced }" 
				  title="Advanced Options"
				>
				  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
					<path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
				  </svg>
				</button>

				<button class="panel-btn" @click="showHelp = true" title="Help">
				  <span><strong>?</strong></span>
				</button>
			  </div>

			  <div class="toolbar-group" v-if="selectedPoints.length > 0">
				<button class="panel-btn" @click="handleDownload" :class="{ 'active': isDownloading }" :disabled="isDownloading" :title="xlsxDownloadLabel">
				   <span v-if="isDownloading" class="spinner-small"></span>
				   <excelIcon v-else class="btn-icon-svg" />
				</button>

				<button class="panel-btn" @click="downloadChartImage" :class="{ 'active': isDownloadingChart }" :disabled="isDownloadingChart" :title="chartDownloadLabel">
				   <span v-if="isDownloadingChart" class="spinner-small"></span>
				   <graphIcon v-else class="btn-icon-svg" />
				</button>

			  </div>

			</div>
			
		</div>
		
		<div v-if="showAdvanced" class="advanced-popup-container">
			<div class="advanced-card">

				<div class="card-header">
					  <strong>Advanced Options</strong>
					  <div class="header-actions">
						<button @click="restoreDefaults" class="btn-restore-link">
						  Restore defaults
						</button>
						<button @click="showAdvanced = false" class="popup-close">&times;</button>
					  </div>
				</div>
				
				<div class="card-body custom-scrollbar">
		  
				<div class="opt-group">
					<label class="group-label">Variables</label>
					<div class="checkbox-grid">
					   <label v-for="v in availableVariable" :key="v" class="checkbox-pill">
						 <input type="checkbox" :value="v" v-model="pendingVariable"> 
						 <span>{{ v.toUpperCase() }}</span>
					   </label>
					</div>
				</div>

				<div class="opt-group">
					<label class="group-label">Processing Level</label>
					<div class="checkbox-grid">
					   <label v-for="q in availableQuality" :key="q" class="checkbox-pill">
						 <input type="checkbox" :value="q" v-model="pendingQuality"> 
							<span>{{ qualityLabels[q] || q }}</span>
					   </label>
					</div>
				</div>
				
				<hr class="divider">
		
				<div class="opt-group">
					<label class="group-label">Parameters</label>
			
					<div class="param-item">
						<div class="param-info">
							<span>Buffer (m)</span>
							<span class="param-val">{{ pendingBuffer }}m</span>
						</div>
						<input type="range" v-model.number="pendingBuffer" min="0" max="5000" step="50" class="modern-slider">
					</div>
			
					<div class="param-item">
						<div class="param-info">
							<span>Gap Fill (Days)</span>
							<span class="param-val">{{ pendingSmoothingParams.gap }}</span>
						</div>
						<input type="range" v-model.number="pendingSmoothingParams.gap" min="1" max="120" class="modern-slider">
					</div>

					<div class="param-item">
						<div class="param-info">
							<span>Window Size (Points)</span>
							<span class="param-val">{{ pendingSmoothingParams.win_raw }}</span>
						</div>
						<input type="range" v-model.number="pendingSmoothingParams.win_raw" min="1" max="121" step="2" class="modern-slider">
					</div>
			
					<div class="param-item">
						<div class="param-info">
							<span>Window Size (Line)</span>
							<span class="param-val">{{ pendingSmoothingParams.win_daily }}</span>
						</div>
						<input type="range" v-model.number="pendingSmoothingParams.win_daily" min="1" max="121" step="2" class="modern-slider">
					</div>

					 <div class="param-item">
						<div class="param-info">
							<span>Polynomial Order</span>
							<span class="param-val">{{ pendingSmoothingParams.poly }}</span>
						</div>
						<input type="range" v-model.number="pendingSmoothingParams.poly" min="1" max="5" class="modern-slider">
					</div>
				</div>
				
			</div>
			
			<div class="card-footer">
			   <button class="btn-primary-action" @click="applyAdvancedOptions" :disabled="isFetching">
				   <span v-if="isFetching" class="spinner-small"></span>
				   <span v-else>Update All Timeseries</span>
			   </button>
			</div>
			
		  </div>
		</div>
			
	</div>
	
	<div class="resize-handle" @mousedown.prevent="startDrag">
       <div class="handle-grip"></div>
    </div>

    <div class="bottom-dashboard" :style="{ height: (100 - mapHeightPercent) + '%' }">
  
		<div class="chart-section">
		  
			<div class="chart-controls-overlay" v-if="selectedPoints.length > 0 && plotOptions.length > 1">
				<span class="overlay-label">Graph View:</span>
				<select v-model="currentPlotVariable" @change="updateChart" class="overlay-select">
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
						<input type="text" v-model.lazy="trendStart" @change="updateTrendCalc" placeholder="Start" class="trend-input"/>
						<span>-</span>
						<input type="text" v-model.lazy="trendEnd" @change="updateTrendCalc" placeholder="End" class="trend-input"/>
					</div>
				</div>
					
			</div>
				
		</div>

		<div class="info-sidebar" v-if="selectedPoints.length > 0">
			
			<div class="info-header">
				<strong>Site List</strong>
			   <button @click="clearAll" class="btn-text-only">Clear All</button>
			</div>

			<div class="info-list-container">
			  <table class="points-table">
				<thead>
				   <tr>
					 <th style="width:8px">#</th>
					 <th>Lat</th>
					 <th>Lon</th>
					 <th>Buffer (m)</th>
					 <th style="width:8px"></th>
				   </tr>
				</thead>
				<tbody>
				  <tr v-for="(point, index) in selectedPoints" :key="point.id">
					 <td :style="{ color: point.color, fontWeight: 'bold', fontSize: '1.1em', textAlign: 'center' }" > {{ index + 1 }} </td>
					 <td><input type="number" v-model.number="point.lat" step="0.001" @change="refreshPointData(point)"></td>
					 <td><input type="number" v-model.number="point.lon" step="0.001" @change="refreshPointData(point)"></td>
					 <td><input type="number" v-model.number.lazy="point.buffer" min="0" step="50" class="table-input" style="text-align: right;" @change="refreshPointData(point)" > </td>
					 <td>
					   <button @click.stop="removePoint(point.id)" class="btn-remove-icon">&times;</button>
					 </td>
				  </tr>
				</tbody>
			  </table>
			</div>

		  </div>
		  
		  <div class="info-sidebar empty" v-else>
			 <p>Select points on the map or upload a file to view data.</p>
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
			Navigate to your preferred ice sheet by clicking the Greenland button 
			( <greenlandIcon class="inline-icon"/> )
			or the Antarctica button
			( <antarcticaIcon class="inline-icon"/> )
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
            <li><strong>Type:</strong> Point or Multipoint geometries only. Maximum of ten points.</li>
          </ul>
		  <p>
            <strong>Optional:</strong>
          </p>
          <ul>
            <li><strong>Buffer:</strong> Include 'buffer' as a field name, containing integer buffer values in metres for each point.</li>
            <li><strong>Point names:</strong> Include 'name' as a field name to give your outputs a custom name.</li>
          </ul>
		  
		  <h3>4. Advanced Options <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg></h3>
		  <p>
			 You can access the advanced options by clicking the 
			 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
			 symbol.
		  </p>
          <p>
		     The advanced options allow you to modify the 'buffer' placed around your selection point 
			 and to select which ice velocity variable(s) and processing level(s) to extract, and allow you to tune the
			 timeseries smoothing parameters. 
		   </p>
		   <p>
			When you modify anything in the advanced options, your choices will be applied to all subsequent extraction locations.
			If you want to apply your advanced options to existing extraction locations, then click "Update All Timeseries".
		   </p>
		   <p>
            <strong>Buffer distance (m):</strong> When you click a location on the map, data are extracted from a small square centred 
			on your chosen point. The size of that square is controlled by the buffer distance text box. The default value is 500 m, which 
			produces a 1000 x 1000 m box (since we buffer outwards by 500 m from the chosen location). If you want to modify the buffer 
			distance for all of the points, just change the value and click "Update All Timeseries". If you want to modify the buffer distance for 
			just one point, then change the value in the Site List table below the map.
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
			Use the slide bars to modify how much smoothing is applied.
          </p>
          <ul>
            <li><strong>Max gap fill length days:</strong> Small gaps in the point data are filled using linear interpolation. Use this option to control the maximum length of gap that is filled.</li>
            <li><strong>Window size days (Points):</strong> Set the size of the moving window used to smooth the point data displayed on the time-series chart. A larger window increases smoothing.</li>
			<li><strong>Window size days (Line):</strong> Set the size of the moving window used to smooth the line data displayed on the time-series chart. A larger window increases smoothing.</li>
			<li><strong>Polynomial order:</strong> Set the degree of the local polynomial fitted to the data within each moving window. A lower order increases smoothing but may distort rapid changes; a higher order better preserved high-frequences features but reduces smoothing.</li>
          </ul>

          <h3>5. Interpreting the Map</h3>
		  <p>
			When you click a point on the map an icon will appear showing the extraction location or region. 
			The icon will usually be a square with a point in the centre: the point shows where you  clicked and the 
			square shows the region in which data were extracted. The size if this square is controlled by the 
			Advanced Options 
			(<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg> ) 
			"Buffer" setting.
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
			<graphIcon class="inline-icon"/> <strong>Download the graph: </strong> 
			You can download the graph showing your data by clicking the 
			<graphIcon class="inline-icon"/>
			button. If one variable or filtering level is selected, this will download a .png of the graph. 
			If multiple variables or filtering levels are selected, this will download a .zip containing one graph per combination of variable and filtering level.
		  </p>
		  <p>
			<excelIcon class="inline-icon"/> <strong>Download the data: </strong>
			You can also download your data to an excel spreadsheet by clicking the 
			<excelIcon class="inline-icon"/>
			button. This will download a .zip containing one excel file per location
			along with a geojson of your point location(s).
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
import domtoimage from 'dom-to-image-more';
import * as XLSX from 'xlsx';
import antarcticaIcon from '../components/icons/antarcticaIcon.vue';
import greenlandIcon from '../components/icons/greenlandIcon.vue';
import excelIcon from '../components/icons/excelIcon.vue';
import graphIcon from '../components/icons/graphIcon.vue';

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
const startPointDrag = (e, index) => {
  // Prevent the click from bubbling to the map (prevents creating a new point)
  L.DomEvent.stopPropagation(e);
  L.DomEvent.preventDefault(e);

  // Disable map panning so the map stays still while we move the box
  if (map.value && map.value.leafletObject) {
    map.value.leafletObject.dragging.disable();
  }
  
  // Set the global cooldown flag immediately
  isDragCooldown.value = true;
  
  // Make sure we use the current version of this point (with the latest coordinates)
  const freshPoint = selectedPoints.value[index];

  // Calculate the difference between the mouse cursor and the shape's center
  // This ensures the shape moves smoothly relative to where you grabbed it
  const mouseLat = e.latlng.lat;
  const mouseLng = e.latlng.lng;

  draggingState.value = {
    active: true,
    point: freshPoint, // Reference to the reactive point object
    offsetLat: freshPoint.lat - mouseLat,
    offsetLon: freshPoint.lon - mouseLng,
	startLat: freshPoint.lat,
    startLon: freshPoint.lon
  };
};

// 2. Move (Attached to the MAP)
const onMapMouseMove = (e) => {
  if (!draggingState.value.active) return;
  
  const state = draggingState.value;
  
  // Find the index of the point we are dragging
  // We use findIndex because we are about to replace the object, 
  // so we need its location in the array.
  const index = selectedPoints.value.findIndex(p => p.id === state.point.id);
  
  if (index === -1) return;

  // 1. Calculate new coordinates
  const newLat = e.latlng.lat + state.offsetLat;
  const newLon = e.latlng.lng + state.offsetLon;

  // 2. Create a BRAND NEW object (Copy + Update)
  // This breaks the reference to the old object. 
  // Vue Production cannot ignore this—it sees a completely new piece of data.
  const updatedPoint = {
      ...selectedPoints.value[index], // Copy existing properties (color, name, etc.)
      lat: newLat,
      lon: newLon
  };

  // 3. Swap the old point for the new one using splice
  // splice matches the array mutation methods Vue watches closely
  selectedPoints.value.splice(index, 1, updatedPoint);

  // 4. Update our drag state to track the NEW object
  // If we don't do this, 'state.point' will still point to the old (stale) object
  state.point = updatedPoint;
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

// --- ADVANCED OPTIONS ---
const showAdvanced = ref(false);

// 1. Define Defaults (Single Source of Truth)
const DEFAULTS = {
  buffer: 500,
  variable: ['s'],
  quality: ['filt'],
  smoothing: { gap: 24, win_raw: 1, win_daily: 25, poly: 2 }
};

// 2. State Definitions 
const availableVariable = ['s', 'u', 'v'];
const availableQuality = ['filt', 'raw'];
const currentPlotVariable = ref('s_filt');    
const pendingBuffer = ref(DEFAULTS.buffer); 
const pendingVariable = ref([...DEFAULTS.variable]); 
const pendingQuality = ref([...DEFAULTS.quality]);
const pendingSmoothingParams = ref({ ...DEFAULTS.smoothing });

// 3. Restore Defaults
// This now updates the "pending" values, so the UI in the popup actually resets.
const restoreDefaults = () => {
  pendingVariable.value = [...DEFAULTS.variable];
  pendingQuality.value = [...DEFAULTS.quality];
  pendingSmoothingParams.value = { ...DEFAULTS.smoothing };
  pendingBuffer.value = DEFAULTS.buffer;
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
    const p = pendingSmoothingParams.value; 
    if (!p) return ''; 
    return `_gf${p.gap}_wr${p.win_raw}_wd${p.win_daily}_p${p.poly}`;
});

// Computed list of available plots based on USER SELECTION
const plotOptions = computed(() => {
    const opts = [];
    pendingVariable.value.forEach(v => { // 1. Iterate only through the user's SELECTED variables
        pendingQuality.value.forEach(q => { // 2. Iterate only through the user's SELECTED qualities
            const labelMap = { s: 'Speed', u: 'Velocity U', v: 'Velocity V' };
            const typeMap = { filt: '(Filtered)', raw: '(Raw)' };
            // 3. Create option only if both parts are selected
            opts.push({ 
                val: `${v}_${q}`, 
                label: `${labelMap[v]} ${typeMap[q]}` 
            });
        });
    });
    return opts;
});

// Ensure currentPlotVariable is valid; if not, reset
watch(plotOptions, (newOpts) => {
    if (newOpts.length > 0 && !newOpts.find(o => o.val === currentPlotVariable.value)) {
        currentPlotVariable.value = newOpts[0].val;
        updateChart();
    }
}, { deep: true });

// Dynamic label for the download button
const xlsxDownloadLabel = computed(() => selectedPoints.value.length > 1 ? 'Download all data (.zip)' : 'Download data (.xlsx)');
const chartDownloadLabel = computed(() => plotOptions.value.length > 1 ? 'Download all graphs (.zip)' : 'Download graph (.png)' );

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

const qualityLabels = {
  'filt': 'Time-filtered',
  'raw':  'Raw Data'  // (Optional: Makes "raw" look nicer too)
};

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


const applyAdvancedOptions = async () => {
  // 1. Validation
  if (pendingVariable.value.length === 0 || pendingQuality.value.length === 0) {
      alert("Warning: You must select at least one Variable and one Processing Level.");
      return; 
  }

  // 2. Define the "Target" Settings
  const targetSettings = {
      buffer: pendingBuffer.value,
      variable: pendingVariable.value,
      quality: pendingQuality.value,
      smoothing: pendingSmoothingParams.value
  };

  // 3. SMART CHECK: Do we *need* to fetch?
  // We check if ANY point is "incompatible" with the new settings.
  // Incompatible = Has different buffer OR different smoothing OR missing variables.
  
  const needsFetch = selectedPoints.value.some(point => {
      const current = point.settings;

      // A. Parameters Changed? (Buffer or Smoothing)
      if (current.buffer !== targetSettings.buffer) return true;
      if (JSON.stringify(current.smoothing) !== JSON.stringify(targetSettings.smoothing)) return true;

      // B. Variables Added? (Target has something Current doesn't)
      const missingVariable = targetSettings.variable.some(v => !current.variable.includes(v));
      if (missingVariable) return true;

      // C. Quality Added?
      const missingQuality = targetSettings.quality.some(q => !current.quality.includes(q));
      if (missingQuality) return true;

      return false; // Point is compatible (it's a superset or exact match)
  });

  // 4. EXECUTE
  if (needsFetch) {
      // Scenario 1: Something fundamental changed or data is missing.
      // We must fetch fresh data for everyone to ensure consistency.
      await refetchAllPoints();
  } else {
      // Scenario 2: Optimization! 
      // We are only REMOVING variables or keeping things same.
      // No server call needed. Just update the settings objects locally.
      
      selectedPoints.value.forEach(point => {
          // Update the settings "metadata" so the chart knows to hide the removed variable
          point.settings = JSON.parse(JSON.stringify(targetSettings));
          point.buffer = targetSettings.buffer;
      });
      
      // Force chart redraw
      updateChart();
      statusMessage.value = "Updated (No fetch needed).";
  }
  
  // Close the modal (optional)
  // showAdvanced.value = false; 
};


// Refetch data for ALL points with the new buffer size and/or new filtering option
const refetchAllPoints = async () => {
  if (selectedPoints.value.length === 0) return;

  isRefreshing.value = true;
  statusMessage.value = "Updating all points...";

  // 1. Prepare the Global Settings (The "New" State)
  const useBuffer = pendingBuffer.value;
  const useVariable = pendingVariable.value;     
  const useQuality = pendingQuality.value; 
  const useSmoothing = { ...pendingSmoothingParams.value }; 
  
  // Define newSettings ---
  // We package these together so we can save them into the point later
  const newSettings = {
    buffer: useBuffer,
    variable: useVariable,
    quality: useQuality,
    smoothing: useSmoothing
  };

  // 2. Prepare ROIs (List of [lat, lon])
  const roiList = selectedPoints.value.map(p => [p.lat, p.lon]);

  trackEvent("data_refresh", {
    event_category: "interaction",
    event_label: "batch_refresh",
    count: roiList.length,
    buffer: useBuffer
  });

  try {
    // 3. Create ONE Payload for ALL points
    const payload = {
      roi: roiList, 
      buffer: useBuffer,
      variable: useVariable,
      quality: useQuality,
      // Expand smoothing params
      gap_fill: useSmoothing.gap,
      win_raw: useSmoothing.win_raw,
      win_daily: useSmoothing.win_daily,
      poly: useSmoothing.poly
    };

    // 4. Single Batch Request
    const response = await apiClient.post('/api/timeseries/json', payload);
    const responseData = response.data; 

    // 5. Map Response back to Points
    // If responseData is an Array:
    const resultsArray = Array.isArray(responseData) 
        ? responseData 
        : Object.values(responseData); // Convert object values to array to guarantee order

    selectedPoints.value.forEach((point, index) => {
        // Get the data corresponding to this point's position in the list
        const newData = resultsArray[index];

        if (newData) {
            // A. Update Raw Data
            point.data = newData;
            
            // B. UPDATE SETTINGS (Deep Copy)
            // Detach this point's settings from the UI state completely
            point.settings = JSON.parse(JSON.stringify(newSettings));
            
            // Sync top-level convenience prop
            point.buffer = newSettings.buffer;
            
            console.log(`Successfully updated point ${index + 1}`);
        } else {
            console.warn(`No data returned for point at index ${index} (ID: ${point.id})`);
        }
    });

    statusMessage.value = "All points updated.";
    updateChart();

  } catch (error) {
    console.error("Batch update failed:", error);
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
  if (pendingVariable.value.length === 0 || pendingQuality.value.length === 0) {
      alert("Warning: Please select at least one Variable and Processing Level in Advanced Options.");
      return;
  }
  
  // 2. PREPARE SETTINGS SNAPSHOT
  // Instead of updating global state, we create a specific settings object 
  // for THIS new point based on the current menu state.
  const newPointSettings = {
      buffer: pendingBuffer.value,
      variable: [...pendingVariable.value],
      quality: [...pendingQuality.value],
      smoothing: { ...pendingSmoothingParams.value }
  };
  
  // 3. Track clicks
  trackEvent("map_click", {
    event_category: "interaction",
    event_label: "extract_timeseries",
    region: currentRegion.value,
    lat: e.latlng.lat.toFixed(4),
    lon: e.latlng.lng.toFixed(4),
    // Optional: You can now log exactly what they requested
    buffer: newPointSettings.buffer
  });
    
  const newId = `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
  
  // 4. FETCH
  // We pass 'newPointSettings' as the 5th argument so the point is created 
  // with these specific options.
  await fetchSinglePoint(
      newId, 
      e.latlng.lat, 
      e.latlng.lng, 
      COLORS[0], // Temporary color (distributeColors will fix it)
      newPointSettings
  );
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

  // 1. Validation
  if (pendingVariable.value.length === 0 || pendingQuality.value.length === 0) {
      alert("Warning: Please select at least one Variable and Processing Level in Advanced Options before uploading.");
      event.target.value = ''; 
      return;
  }

  // 2. Prepare Settings Snapshot (Crucial for chart to work!)
  const uploadSettings = {
      buffer: pendingBuffer.value,
      variable: [...pendingVariable.value],       
      quality: [...pendingQuality.value], 
      smoothing: { ...pendingSmoothingParams.value } 
  };

  isUploading.value = true;
  statusMessage.value = "Uploading...";

  const formData = new FormData();
  formData.append("file", file);
  formData.append("buffer", uploadSettings.buffer);
  
  // Append arrays
  uploadSettings.variable.forEach(v => formData.append("variable", v));
  uploadSettings.quality.forEach(q => formData.append("quality", q));
  
  // Append smoothing
  formData.append("gap_fill", uploadSettings.smoothing.gap);
  formData.append("win_raw", uploadSettings.smoothing.win_raw);
  formData.append("win_daily", uploadSettings.smoothing.win_daily);
  formData.append("poly", uploadSettings.smoothing.poly);

  try {
    const response = await apiClient.post('/api/timeseries/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    const results = response.data;
    if (results.status === 'error') throw new Error(results.message);

    // 3. Process results (Fast Loop)
    const entries = Object.entries(results);
    let addedCount = 0;

    // We can use a simple loop without 'await' for speed
    for (const [siteName, data] of entries) {
        // Stop if we hit the limit
        if (selectedPoints.value.length >= 10) break;

        const ptLat = data.meta?.lat || 0;
        const ptLon = data.meta?.lon || 0;
        
        // Handle buffer logic
        const metaBuffer = data.meta?.buffer_used;
        const siteSpecificBuffer = (metaBuffer !== undefined && metaBuffer !== null) 
            ? Number(metaBuffer) 
            : Number(pendingBuffer.value);

        const color = COLORS[selectedPoints.value.length % COLORS.length];

        // Create and push the point
        selectedPoints.value.push({
            id: Date.now() + addedCount, // Ensure unique IDs
            lat: ptLat,
            lon: ptLon,
            color: color,
            data: data,
            name: siteName,
            buffer: siteSpecificBuffer,
            settings: JSON.parse(JSON.stringify(uploadSettings)) // Deep copy settings
        });

        addedCount++;
    }

    statusMessage.value = `Loaded ${addedCount} sites.`;
    updateChart();
    event.target.value = ''; // Reset file input

  } catch (error) {
    console.error(error);
    statusMessage.value = "Upload failed.";
    alert("Upload failed: " + (error.message || "Unknown error"));
  } finally {
    isUploading.value = false;
  }
};


// Fetch data for a single point (used by Map Click)
const fetchSinglePoint = async (id, lat, lon, color, customSettings = null) => {
  isFetching.value = true;
  statusMessage.value = "Fetching...";
  
  // BEHAVIOUR 1 LOGIC:
  // If customSettings is null (New Point Click), snapshot the current Advanced Options.
  // If customSettings exists (Refresh or Mass Update), use those.
  const settings = customSettings || {
      buffer: pendingBuffer.value,
      variable: [...pendingVariable.value],
      quality: [...pendingQuality.value],
      smoothing: { ...pendingSmoothingParams.value }
  };
  
  // Track data fetching
  trackEvent("data_fetch", {
	  event_category: "interaction",
	  event_label: "data_fetch",
	  buffer: settings.buffer,
      variable: settings.variable,
      quality: settings.quality,
      region: currentRegion.value,
	  lat: lat,
	  lon: lon
	});
  
  // Ping the backend
  try {
    const payload = { 
        roi: [[lat, lon]], 
        buffer: settings.buffer,
        variable: settings.variable, 
        quality: settings.quality,
        gap_fill: settings.smoothing.gap,
        win_raw: settings.smoothing.win_raw,
        win_daily: settings.smoothing.win_daily,
        poly: settings.smoothing.poly
    };
    const response = await apiClient.post('/api/timeseries/json', payload);
    const rawData = response.data;
    const firstKey = Object.keys(rawData)[0];
    const siteData = rawData[firstKey];
	
	// Check for ping errors
    if (siteData.status === 'error') {
      statusMessage.value = `Error: ${siteData.message}`; return;
    }
	
	// Save the snapshot
    // We store 'settings' inside the point. This freezes the configuration 
    // for this specific point until the user explicitly changes it.
    const newPoint = { id, lat, lon, color, settings: settings, buffer: settings.buffer, data: siteData, name: firstKey };
	
	// Record
    const idx = selectedPoints.value.findIndex(p => p.id === id);
    if (idx >= 0) selectedPoints.value[idx] = newPoint;
    else selectedPoints.value.push(newPoint);
	
	// Show status
    statusMessage.value = "Loaded.";
    updateChart();
  } catch (error) {
    console.error(error); statusMessage.value = "Server Error.";
  } finally {
    isFetching.value = false;
  }
};

// Wrapper for updating a point when coords are manually edited
const refreshPointData = async (point) => {
    // Construct settings using the point's existing variables/smoothing
    // but the new buffer from the input box.
    const updatedSettings = {
        ...point.settings, // Copy old variable, quality, smoothing
        buffer: point.buffer // Use the new buffer value
    };
    
    // Pass these settings back to fetchSinglePoint
    await fetchSinglePoint(point.id, point.lat, point.lon, point.color, updatedSettings);
};
const removePoint = (id) => { selectedPoints.value = selectedPoints.value.filter(p => p.id !== id); distributeColors(); updateChart(); };
const clearAll = () => { selectedPoints.value = []; Plotly.purge('velocity-chart'); };



// --- CHART PLOTTING (PLOTLY) ---
// BUILD CHART DATA (Returns {data, layout} for a given quality level)
const buildChartConfig = (plotKey) => {
  const traces = [];
  
  // Reset Legend Items
  legendItems.value = [];
  
  // 1. PREPARE KEYS FOR FILTERING
  // Split 's_filt' into 's' and 'filt'
  const [targetVariable, targetQuality] = plotKey.split('_'); 

  selectedPoints.value.forEach((point, idx) => {
    // A. DATA EXISTENCE CHECK (Existing)
    if (point.data.status === 'error' || !point.data.data) return;
    
    // B. SETTINGS CHECK (New "Visual Filtering")
    // Ensure we have settings (fallback for safety)
    const settings = point.settings || { variable: [], quality: [] };
    
    // Check if this specific variable/quality combination is enabled for this point
    const isEnabled = settings.variable.includes(targetVariable) && 
                      settings.quality.includes(targetQuality);

    // If data is missing OR user disabled this variable, skip it.
    if (!point.data.data[plotKey] || !isEnabled) return;

    // Load data and check
    const varData = point.data.data[plotKey];
    const rootData = point.data.data;
    if (!varData) return;
	
	// Setup styles
    const pale = makePale(point.color);
    const label = /^Site_\d+$/.test(point.name) ? `Site${idx+1}` : point.name;
    //const suffix = plotKey.includes('raw') ? ' (Raw)' : ''; // uncomment if you want raw next to each legend item
	const suffix = plotKey.includes('raw') ? '' : '';
	
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
  if (plotKey.startsWith('s') && plotKey.includes('raw')) yAxisLabel = "Raw speed (m/yr)"; 
  else if (plotKey.startsWith('s')) yAxisLabel = "Filtered speed (m/yr)";
  else if (plotKey.startsWith('u') && plotKey.includes('raw')) yAxisLabel = "Raw easting velocity (m/yr)"; 
  else if (plotKey.startsWith('u')) yAxisLabel = "Filtered easting velocity (m/yr)";
  else if (plotKey.startsWith('v') && plotKey.includes('raw')) yAxisLabel = "Raw northing velocity (m/yr)"; 
  else if (plotKey.startsWith('v')) yAxisLabel = "Filtered northing velocity (m/yr)";
  
  // Define the SVG Data URI for the word "SHIVER"
	const watermarkSvg = `
	  <svg xmlns="http://www.w3.org/2000/svg" width="100" height="20" viewBox="0 0 100 20">
		<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
			  font-family="sans-serif" font-weight="900" font-size="18" 
			  fill="rgba(135, 206, 235, 0.15)">
		  S H I V E R
		</text>
	  </svg>`;

	// Convert it to a Base64 string for Plotly
	const watermarkUrl = "data:image/svg+xml;base64," + btoa(watermarkSvg);

  const layout = {
	images: [
		{
		  source: watermarkUrl,
		  xref: "paper", yref: "paper",
		  x: 0.5, y: 0.5,
		  sizex: 0.8, sizey: 0.8, // 80% of the chart width/height
		  xanchor: "center", yanchor: "middle",
		  layer: "below",
		  opacity: 1 // Opacity is handled inside the SVG fill color
		}
	],
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
  
  // Handle empty state
  if (selectedPoints.value.length === 0) { 
      Plotly.purge('velocity-chart'); 
      legendItems.value = []; 
      xAxisMin.value = ''; xAxisMax.value = '';
      yAxisMin.value = ''; yAxisMax.value = '';
      isUserZoomed.value = false;
      return; 
  }
  
  // Build data and configuration
  const { data, layout } = buildChartConfig(currentPlotVariable.value);
  
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
  
  // Adjust plotly configuration
  const config = {
    responsive: true,
	displayModeBar: true,
	displaylogo: false,
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
	// -- Add your custom button
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
  };
  
  // Render the plot
  const graphDiv = await Plotly.newPlot('velocity-chart', data, layout, config);
  
  //Attach listener for axis updates
  if (graphDiv) {
    graphDiv.removeAllListeners && graphDiv.removeAllListeners('plotly_relayout');
    graphDiv.on('plotly_relayout', onPlotRelayout);
    
    // Populate initial values if not zoomed
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


// CHART IMAGE DOWNLOAD (MULTI-FILE + OPTIMIZED SNAPSHOT)
const downloadChartImage = async () => {
  if (selectedPoints.value.length === 0) return;

  // 1. Identify Elements
  const chartContainer = document.querySelector('.chart-section'); 
  const graphDiv = document.getElementById('velocity-chart'); // The specific Plotly div

  if (!chartContainer || !graphDiv) {
      console.error("Could not find chart elements.");
      alert("Error: Chart container not found.");
      return;
  }

  statusMessage.value = "Processing charts...";
  setWaitCursor(true);
  
  // High quality scale
  const EXPORT_SCALE = 1.5; 
  const originalPlotVariable = currentPlotVariable.value;

  // 2. Wrap in timeout to allow UI to show "Processing..."
  setTimeout(async () => {
    let tempImg = null;
    const originalDisplay = graphDiv.style.display; // Remember original display state

    try {
      const zip = new JSZip();
      
      // Determine which variables to process
      const optionsProcess = plotOptions.value.length > 0 
          ? plotOptions.value 
          : [{val: currentPlotVariable.value, label: 'Current'}];
      
      const filesToSave = [];

      // --- START LOOP ---
      for (const opt of optionsProcess) {
        statusMessage.value = `Capturing ${opt.label || opt.val}...`;

        // A. Switch View & Wait for Render
        // We still need to do this so Plotly calculates the new trend lines/data
        if (currentPlotVariable.value !== opt.val) {
            currentPlotVariable.value = opt.val;
            await nextTick();
            if (typeof updateChart === 'function') await updateChart();
            // Wait for Plotly animation/render to settle
            await new Promise(r => setTimeout(r, 800)); 
        }

        // B. Snapshot Plotly Vectors to PNG
        const plotlyDataUrl = await Plotly.toImage(graphDiv, {
            format: 'png',
            width: graphDiv.clientWidth * EXPORT_SCALE,
            height: graphDiv.clientHeight * EXPORT_SCALE,
            scale: 1 
        });

        // C. Swap: Hide Interactive Graph, Show Static Image
        tempImg = document.createElement('img');
        tempImg.src = plotlyDataUrl;
        tempImg.style.width = '100%'; 
        tempImg.style.height = '100%';
        tempImg.style.objectFit = 'contain';
        tempImg.style.display = 'block';
        
        // Insert Image, Hide Graph
        graphDiv.parentNode.insertBefore(tempImg, graphDiv);
        graphDiv.style.display = 'none';

        // D. Capture Container (Legend + Static Image)
        // dom-to-image is now instant because it doesn't see vectors
        const width = chartContainer.clientWidth;
        const height = chartContainer.clientHeight;

        const imgUrl = await domtoimage.toPng(chartContainer, {
            bgcolor: '#FFFFFF', 
            width: width * EXPORT_SCALE,
            height: height * EXPORT_SCALE,
            style: {
              transform: `scale(${EXPORT_SCALE})`,
              transformOrigin: 'top left',
              width: `${width}px`,
              height: `${height}px`
            },
            filter: (node) => {
                // 1. Standard Checks
                if (!node.classList) return true; 

                // 2. Exclude the hidden graphDiv so dom-to-image doesn't process it
                if (node.id === 'velocity-chart') return false; 

                // 3. Exclude UI/Dashboard Elements
                if (node.classList.contains('chart-controls')) return false;
                if (node.classList.contains('chart-controls-overlay')) return false;
                if (node.classList.contains('axis-inputs')) return false; 
                if (node.classList.contains('info-sidebar')) return false;

                // 4. Exclude Inputs/Buttons
                const tag = node.tagName;
                if (['INPUT', 'SELECT', 'BUTTON', 'TEXTAREA'].includes(tag)) return false;
                if (tag === 'LABEL' && node.parentElement.classList.contains('axis-group')) return false;

                return true;
            }
        });

        // E. Store Result
        const blob = await (await fetch(imgUrl)).blob();
        
        // Handle suffix safely
        const suffix = (typeof smoothingSuffix !== 'undefined' && smoothingSuffix.value) ? smoothingSuffix.value : '';
        const fname = `velocity_${opt.val}_timeseries${suffix}.png`;
        
        filesToSave.push({ name: fname, blob: blob });

        // F. Cleanup for next iteration
        // Remove temp image and show graph again so the next 'updateChart' works
        if (tempImg) tempImg.remove();
        graphDiv.style.display = originalDisplay;

        // Pause briefly to let browser breathe (prevents "Page Unresponsive")
        await new Promise(resolve => setTimeout(resolve, 50)); 
      }
      // --- END LOOP ---

      // 3. Restore Original State
      if (currentPlotVariable.value !== originalPlotVariable) {
          currentPlotVariable.value = originalPlotVariable;
          await nextTick();
          if (typeof updateChart === 'function') await updateChart();
      }

      // 4. Save/Zip
      if (filesToSave.length === 1) {
        saveAs(filesToSave[0].blob, filesToSave[0].name);
        statusMessage.value = "Chart downloaded.";
      } else {
        statusMessage.value = "Compressing...";
        filesToSave.forEach(f => zip.file(f.name, f.blob));
        const content = await zip.generateAsync({type:"blob"});
        saveAs(content, `Velocity_Charts_${currentRegion.value}.zip`);
        statusMessage.value = "All charts downloaded.";
      }

    } catch (error) {
      console.error("Chart Export Error:", error);
      statusMessage.value = "Error generating chart.";
    } finally {
      // Final safety cleanup
      if (tempImg && tempImg.parentNode) tempImg.remove();
      if (graphDiv) graphDiv.style.display = originalDisplay;

      setWaitCursor(false);
      setTimeout(() => statusMessage.value = "", 2000);
    }
  }, 50);
};


// Helper: Generates filenames for download
const getFilename = (p, index) => {
  const meta = p.data.meta || {};
  let name = meta.site_name || p.name || 'Site';
  if (/^Site_\d+$/.test(name)) name = `Site_${index + 1}`;
  const buf = meta.buffer_used !== undefined ? meta.buffer_used : pendingBuffer.value;
  // Use toFixed(3) for lat/lon as requested previously + params
  const lat = p.lat.toFixed(3);
  const lon = p.lon.toFixed(3);
  return `${name}_${buf}m_${lat}_${lon}${smoothingSuffix.value}.xlsx`;
};

// --- DATA DOWNLOAD HANDLER ---
const handleDownload = async () => {
  if (selectedPoints.value.length === 0) return;

  // Track downloads (Always a ZIP now)
  trackEvent("file_download", {
      event_category: "export",
      event_label: "zip_data_package", 
      file_extension: "zip", 
      file_name: selectedPoints.value.length === 1 
          ? `${getFilename(selectedPoints.value[0], 0)}_package` 
          : "velocity_data_batch",
      region: currentRegion.value,
      count: selectedPoints.value.length
  });

  isDownloading.value = true;
  
  try {
    const zip = new JSZip();
    
    // 1. Add XLSX Files to Zip
    selectedPoints.value.forEach((p, index) => {
      // Pass index (will be 0 if single file)
      const wb = generateXLSX(p, index);
      const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
      zip.file(getFilename(p, index), wbout);
    });

    // 2. Add GeoJSON Summary (Always included)
    const geojson = {
      type: "FeatureCollection",
      features: selectedPoints.value.map((p, index) => {
        let name = p.name || `Site_${p.id}`;
        // Logic to ensure clean naming if default IDs are used
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
            buffer_m: p.data.meta?.buffer_used || pendingBuffer.value,
            region: currentRegion.value
          }
        };
      })
    };

    zip.file("sites.geojson", JSON.stringify(geojson, null, 2));

    // 3. Generate and Save
    const content = await zip.generateAsync({ type: "blob" });
    
    // Determine Filename:
    // If single file, use that site's name + "_data.zip"
    // If multiple, use generic "batch.zip"
    let zipName = "velocity_data_batch.zip";
    
    if (selectedPoints.value.length === 1) {
        const baseName = getFilename(selectedPoints.value[0], 0).replace('.xlsx', '');
        zipName = `${baseName}_data.zip`;
    }

    saveAs(content, zipName);

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
      ["Buffer (m)", meta.buffer_used || pendingBuffer.value],
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
  position: absolute; top: 5px; right: 35px; z-index: 100;  display: flex; 
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
@media (max-height: 900px) {
  
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
    
    /* THE MAGIC SAUCE:
       1. opacity: fade out over 0.3s... AFTER waiting 0.5s
       2. visibility: switch to hidden... AFTER waiting 0.8s (0.5 + 0.3)
       
       This keeps the buttons interactive during the delay!
    */
    transition: 
      opacity 0.3s ease 0.5s, 
      visibility 0s linear 0.8s;
  }

  /* 3. On Hover: Reveal the tools */
  .map-toolbar:hover .tools-wrapper {
    /* Visible state */
    opacity: 1;
    visibility: visible;
    
    /* Show immediately (no delay) */
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
.bottom-dashboard {
  display: flex;
  width: 100%;
  background: white;
  border-top: 1px solid #ddd;
  overflow: hidden; /* Prevent double scrollbars */
}

/* Left: Chart */
.chart-section {
  flex: 1; /* Takes all available space */
  position: relative;
  min-width: 0; /* Flexbox safety */
  padding: 10px;
  display: flex;
  flex-direction: column;
}

/* Right: Site Info Sidebar */
.info-sidebar {
  width: 300px; /* Fixed width for the list */
  border-left: 1px solid #eee;
  display: flex;
  flex-direction: column;
  background: #f9f9f9;
}

.info-sidebar.empty {
  align-items: center;
  justify-content: center;
  color: #999;
  font-style: italic;
  padding: 20px;
  text-align: center;
}

/* Info Header (Buffer + Clear) */
.info-header {
  padding: 10px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.info-header input {
  width: 60px;
  margin-left: 5px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.btn-text-only {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 0.8rem;
  font-weight: bold;
  cursor: pointer;
}
.btn-text-only:hover { text-decoration: underline; }

/* Scrollable List Area */
.info-list-container {
  flex: 1; /* Fills remaining vertical space */
  overflow-y: auto;
  padding: 0;
}

/* Compact Table Styling */
.points-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.points-table th {
  text-align: left;
  padding: 8px;
  background: #eee;
  color: #666;
  font-weight: 600;
  position: sticky;
  top: 0;
}

.points-table td {
  padding: 6px 8px;
  border-bottom: 1px solid #f0f0f0;
}

.points-table input {
  width: 100%;
  border: 1px solid transparent;
  background: transparent;
  font-family: monospace;
}
.points-table input:focus {
  border-color: #3498db;
  background: white;
}

.btn-remove-icon {
  border: none;
  background: none;
  color: #999;
  font-size: 1.2rem;
  cursor: pointer;
  line-height: 1;
}
.btn-remove-icon:hover { color: #e74c3c; }

/* --- MOBILE RESPONSIVENESS FOR BOTTOM-DASHBOARD --- */
@media (max-width: 768px) {
  
  /* 1. Stack the dashboard vertically */
  .bottom-dashboard {
    flex-direction: column;
    /* Allow the dashboard container to scroll vertically 
       because the stacked content (Chart + List) might be taller 
       than the allocated screen height */
    overflow-y: auto !important; 
    overflow-x: hidden;
  }

  /* 2. Give the chart a fixed height */
  .chart-section {
    width: 100%;
    /* flex: none ensures it doesn't try to shrink to fit the screen.
       It will force the dashboard to scroll if needed. */
    flex: none; 
    height: 350px; /* Enough space for Plotly to be readable */
    border-bottom: 1px solid #ddd;
  }

  /* 3. Make the sidebar full width */
  .info-sidebar {
    width: 100%;
    height: auto; /* Let it grow based on content */
    border-left: none; /* Remove side border */
    border-top: 1px solid #eee; /* Add top border */
    flex: none;
  }

  /* 4. Restrict the table height (Optional) */
  /* This prevents the table from becoming 5000px long if you have many points,
     forcing the user to scroll forever to get back to the chart. */
  .info-list-container {
    max-height: 300px; 
    overflow-y: auto;
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



/* --- 3. MODERN ADVANCED POPUP --- */

/* 1. The Invisible Container */
/* This centers the popup but lets clicks pass through to the map */
.advanced-popup-container {
  position: absolute;
  
  /* Fill the entire parent (.map-wrapper) */
  inset: 0;  /* Short for top:0; right:0; bottom:0; left:0; */
  
  z-index: 2000;
  pointer-events: none; /* KEY: Allows clicking the map behind! */
  
  display: flex;
  justify-content: center;
  align-items: flex-start; /* Aligns to top, but with margin */
  padding-top: 60px; /* Space from the top of the map */
  padding-bottom: 20px; /* Space from bottom of map */
}

/* 2. The Card Itself */
.advanced-card {
  pointer-events: auto; /* Re-enable clicks inside the card */
  width: 380px;
  max-width: 90%;
  max-height: 95%; 
  display: flex;
  flex-direction: column; /* Stack Header, Body, Footer */
  
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px); /* Modern frosted glass effect */
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.05);
  overflow: hidden; /* Clips children to rounded corners */
  
  /* Slide-in Animation */
  animation: slideDown 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* --- HEADER --- */
.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid rgba(0,0,0,0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}
.card-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.btn-restore {
  background: none;
  border: none;
  color: #95a5a6;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: underline;
}
.btn-restore:hover { color: #e74c3c; }
.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  color: #bdc3c7;
  cursor: pointer;
  padding: 0;
}
.btn-close:hover { color: #2c3e50; }

/* --- BODY (SCROLLABLE) --- */
.card-body {
  flex: 1; /* Fills available space */
  overflow-y: auto; /* Scrolls if content is too tall */
  padding: 20px;
}

.opt-group { margin-bottom: 20px; }
.group-label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #95a5a6;
  font-weight: 700;
  margin-bottom: 10px;
}
.divider {
  border: 0;
  border-top: 1px solid rgba(0,0,0,0.06);
  margin: 20px 0;
}

/* Modern Checkbox "Pills" */
.checkbox-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.checkbox-pill {
  position: relative;
  cursor: pointer;
}
.checkbox-pill input {
  position: absolute; opacity: 0; width: 0; height: 0;
}
.checkbox-pill span {
  display: inline-block;
  padding: 6px 12px;
  background: #f1f3f5;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #555;
  transition: all 0.2s;
  border: 1px solid transparent;
}
/* Selected State */
.checkbox-pill input:checked + span {
  background: #e8f4fd;
  color: #3498db;
  border-color: #3498db;
  font-weight: 500;
}

/* Sliders */
.param-item { margin-bottom: 12px; }
.param-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #2c3e50;
  margin-bottom: 4px;
}
.param-val { font-weight: 600; color: #3498db; }

.modern-slider {
  -webkit-appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #e0e0e0;
  outline: none;
}
.modern-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #3498db;
  cursor: pointer;
  transition: transform 0.1s;
}
.modern-slider::-webkit-slider-thumb:hover { transform: scale(1.2); }

/* --- FOOTER --- */
.card-footer {
  padding: 15px 20px;
  background: white;
  border-top: 1px solid rgba(0,0,0,0.06);
}
.btn-primary-action {
  width: 100%;
  padding: 10px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary-action:hover { background: #34495e; }
.btn-primary-action:disabled { background: #95a5a6; cursor: not-allowed; }

/* Custom Scrollbar for the body */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: rgba(0,0,0,0.1); border-radius: 3px; }

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
.coord-input { width: 70px; padding: 4px; font-size: 0.85rem; border: 1px solid #ddd; border-radius: 3px; }
.btn-remove { border: none; background: transparent; color: #999; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; padding: 4px; border-radius: 4px; transition: all 0.2s ease; }
.btn-remove:hover { color: #dc3545; background-color: rgba(220, 53, 69, 0.1); }

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
  font-size: 0.95rem;
  font-weight: 600;
  color: #333;
}

.legend-trend {
  font-weight: 400; /* Normal weight for stats */
  font-size: 0.8em; /* Slightly smaller */
  margin-top: -1px;
}

.legend-global-key {
  position: absolute;
  top: 100%; 
  left: 70px; 
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

/* --- PLOTLY TOOLBAR OVERRIDES --- */

/* 1. Force the toolbar to the top-right corner */
.js-plotly-plot .plotly .modebar {
    position: absolute;
    top: 10px !important;      /* Pin to very top */
    right: 20px !important;    /* Pin to very right */
    left: auto !important;
    
    /* Optional: Add a background so lines don't show through if they go high */
    background: rgba(255, 255, 255, 0.8) !important; 
}

/* 2. (Optional) Adjust the spacing of the icons */
.js-plotly-plot .plotly .modebar-group {
    background: transparent !important;
    padding-top: 0px !important; /* Centers buttons vertically in the margin space */
}

</style>