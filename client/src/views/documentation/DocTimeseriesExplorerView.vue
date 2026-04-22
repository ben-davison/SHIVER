<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'

// Icons
import greenlandIcon from '../../components/icons/greenlandIcon.vue';
import antarcticaIcon from '../../components/icons/antarcticaIcon.vue';
import excelIcon from '../../components/icons/excelIcon.vue';
import graphIcon from '../../components/icons/graphIcon.vue';

const route = useRoute()

// Handles URL hash jumping on first load
onMounted(() => {
  if (route.hash) {
    nextTick(() => {
      setTimeout(() => {
        const element = document.getElementById(route.hash.slice(1))
        if (element) {
          const headerOffset = 100;
          const elementPosition = element.getBoundingClientRect().top;
          const offsetPosition = elementPosition + window.scrollY - headerOffset;
          window.scrollTo({ top: offsetPosition, behavior: "smooth" });
        }
      }, 100)
    })
  }
})
</script>

<template>
  <div class="doc-inner-page">
  
    <section id="SHIVER Timeseries">
          <h1>Introduction</h1>
          <p class="intro-text">
            Welcome to the technical documentation for <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR).
            SHIVER allows you to explore and download a multitude of ice velocity measurements for Greenland and Antarctica using one simple interface.
          </p>
		  <br>
    </section>
    
    <section id="basic-usage">
		  <h3>6.1. Basic Usage</h3>
		  <p>
			The SHIVER Timeseries Explorer lets you quickly and easily visualize and export ice velocity timeseries
			anywhere on the Greenland and Antarctic ice sheets. Just navigate to your glacier of interest and click on the map 
			to create a chart showing how ice flow has changed over time in that location. 
			After selecting a point, you can click-and-drag it to modify the position, or you can manually modify the coordinates in the site list. 
			Alternatively, you can upload a shapefile containing a point or points to view time-series of ice velocity in those locations. 
			You can select up to ten points to compare different locations.
		  </p>
		  <p>
			SHIVER allows you to examine ice flow changes in Greenland or Antarctica. You can navigate to your preferred ice sheet by clicking the Greenland button 
			(<greenlandIcon class="inline-icon"/>)
			or the Antarctica button
			(<antarcticaIcon class="inline-icon"/>)
		  </p>
		  <p>
			<strong>The timeseries chart:</strong> After creating a chart you can click-and-drag in the chart area to zoom in on a particular section of the chart. 
			Double click on the chart to reset the axes. Or use the zoom, pan and reset buttons in the top right of the chart to navigate. 
			You can click the 
			(<svg class="inline-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
			  <path fill="currentColor" d="M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10c1.21,0,2.12-1.07,1.86-2.26c-0.08-0.34-0.24-0.66-0.45-0.92 C13.2,18.55,13.06,18.27,13.06,18c0-0.55,0.45-1,1-1h1.56c3.53,0,6.38-2.85,6.38-6.38C22,5.46,17.52,2,12,2z M6.5,11.5 c-0.83,0-1.5-0.67-1.5-1.5s0.67-1.5,1.5-1.5s1.5,0.67,1.5,1.5S7.33,11.5,6.5,11.5z M9.5,7.5C8.67,7.5,8,6.83,8,6s0.67-1.5,1.5-1.5 s1.5,0.67,1.5,1.5S10.33,7.5,9.5,7.5z M14.5,7.5C13.67,7.5,13,6.83,13,6s0.67-1.5,1.5-1.5s1.5,0.67,1.5,1.5S15.33,7.5,14.5,7.5z M17.5,11.5c-0.83,0-1.5-0.67-1.5-1.5s0.67-1.5,1.5-1.5s1.5,0.67,1.5,1.5S18.33,11.5,17.5,11.5z"/>
			</svg>)
			icon to colour the data points either by site number or by data source. 
		  </p>
		  <br>
    </section>
		  
	<section id="file-upload">
			<h3>6.2. Uploading Files   
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
		  <br>
	</section>
	
	<section id="advanced-options">
		  <h3>6.3. Advanced Options <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg></h3>
		  <p>
			 You can access the advanced options by clicking the 
			 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
			 symbol.
		  </p>
          <p>
		     The advanced options allow you to control which datasets are extracted from our data centre and how they are filtered before being displayed in the chart.
             You can choose whether to query only our SHIFT dataset or whether to query our 'multi-source' dataset. The multi-source dataset is the default. 
		   </p>
		   <p>
		     When querying the multi-source dataset, you can select which data source(s) to extract. See the <AppLink to="/documentation/greenland"class="text-link">Greenland Data</AppLink> and 
			 <AppLink to="/documentation/antarctic"class="text-link">Antarctic Data</AppLink> documentation pages for details of each data source. 
		   </p>
		   <p>
			 When querying only the SHIFT dataset, you can select which ice velocity variable(s) and processing level(s) to extract. 
			 See the <AppLink to="/documentation/shift"class="text-link">SHIFT</AppLink> documentation page for details of velocity variables and processing levels.
		   </p>
		   <p>
			 For either dataset, you can modify the parameters used during the ice velocity extraction and filtering. You can adjust the 'buffer' placed around your selection point 
			 - larger buffers extract data from larger squares around your selection point. You can also adjust the timeseries smoothing parameters, such as the size of data gaps 
			 to fill and the size of the window used in the time-series smoothing. 
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
			See the <AppLink to="/documentation/shift#mosaics" class="text-link">Mosaics section of our SHIFT Documentation page</AppLink> for more details.
          </p>
          <ul>
            <li><strong>Raw:</strong> Extract velocity from our 'raw' date-pair velocity mosaics.</li>
            <li><strong>Time-filtered:</strong> Extract velocity from our 'time filtered' date-pair velocity mosaics.</li>
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
		  <br>
	</section>

	<section id="map-interpret">
          <h3>6.4. Navigating & Interpreting the Map</h3>
		  <p>
		    When you first access the SHIVER Timeseries Explorer, you will see a map of Greenland with a long-term average ice speed estimate overlain. 
			You can switch to a map of Antarctica by clicking the Antarctica button (<antarcticaIcon class="inline-icon"/>) in the top-right of the map, or
			switch back to Greenland by clicking the Greenland button (<greenlandIcon class="inline-icon"/>).
		  </p>
		  <p>
		    You can navigate the map by using your mouse scroller and by clicking and dragging the cursor to move around. 
          </p>
		  <br>
		  <p>
            <strong>Data overlays:</strong> A long-term average ice speed estimate is shown on the map by default. You can remove that layer and display
            other overlays by clicking the "Map Layers & Analysis" button 
            (<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
				<polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
				<polyline points="2 12 12 17 22 12"></polyline>
				<polyline points="2 17 12 22 22 17"></polyline>
			</svg>). 
			There are two modes of layers: "Overview" layers and "Analysis" layers. 
	       </p>
		   <p>
		     <strong>Overview layers</strong>
		   </p>
		   <p>
		      The overview layers panel allows you to control the basemap and long-term average overlays of certain variables, as well as display contextual information like glacier basin outlines.
		   </p>
		   <ul>
			  <li><em>Satellite basemap:</em> A 20 m resolution image mosaic created from true-colour Sentinel-2 imagery acquired during June 1st to August 31st in 2023, 2024 and 2025. This is only available for Greenland.</li>
			  <li><em>Topography basemap:</em> A hillshaded digital elevation model of each ice sheet (Howat et al., <AppLink to="https://nsidc.org/data/nsidc-0645/versions/1" target="_blank" rel="noopener" class="text-link">2015</AppLink>, <AppLink to="https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/EBW8UC" target="_blank" rel="noopener" class="text-link">2022</AppLink>).</li>
			  <li><em>Speed overlay:</em> The average ice speed from all available datasets, in metres per year.</li>
              <li><em>Measurement Count overlay:</em> The number of valid speed measurements available in each location.</li>
			  <li><em>Speed Trend overlay:</em> The linear trend in speed through all available measurements, in metres per year per year.</li>
			  <li><em>Measurement Range overlay:</em> The median spread of speed estimates between data sources during common time periods.</li>
			  <li><em>Flow direction:</em> The long term average flow direction of each ice sheet displayed using vector arrows.</li>
			  <li><em>Ice Margins:</em> This uses simplified versions of the PROMICE 2022 ice mask (<AppLink to="https://essd.copernicus.org/articles/18/411/2026/essd-18-411-2026.html" target="_blank" rel="noopener" class="text-link">Luetzenburg et al., 2025</AppLink>) for Greenland, 
			          the ADD SCAR medium resolution Antarctic coastline (<AppLink to="https://data.bas.ac.uk/items/f2792d06-1e9d-4e00-a5c6-37d43bee5297/" target="_blank" rel="noopener" class="text-link">Gerrish et al., 2025</AppLink>) and the grounding line of <AppLink to="https://tc.copernicus.org/articles/18/4723/2024/" target="_blank" rel="noopener" class="text-link">Wallis et al. (2024)</AppLink></li>
			  <li><em>Basin Outlines:</em> For Greenland, the basin options are the 
              <AppLink to="https://imbie.org/" target="_blank" rel="noopener" class="text-link">IMBIE</AppLink> basins (<AppLink to="https://datadryad.org/dataset/doi:10.7280/D1WT11" target="_blank" rel="noopener" class="text-link">Mouginot et al., 2019</AppLink>), the
			  glacier catchments within each IMBIE basin (<AppLink to="https://datadryad.org/dataset/doi:10.7280/D1WT11" target="_blank" rel="noopener" class="text-link">Mouginot et al., 2019</AppLink>) or individual glacier basins (<AppLink to="https://essd.copernicus.org/articles/12/2811/2020/" target="_blank" rel="noopener" class="text-link">Mankoff et al., 2020</AppLink>; <AppLink to="https://dataverse.geus.dk/dataset.xhtml?persistentId=doi:10.22008/FK2/XKQVL7" target="_blank" rel="noopener" class="text-link">Mankoff, 2020</AppLink>). For Antarctica,
			  the basin options are those used in IMBIE (<AppLink to="https://nsidc.org/data/nsidc-0709/versions/2" target="_blank" rel="noopener" class="text-link">Mouginot et al., 2017</AppLink>), the glacier catchments within each IMBIE basin (<AppLink to="https://nsidc.org/data/nsidc-0709/versions/2" target="_blank" rel="noopener" class="text-link">Mouginot et al., 2017</AppLink>) or individual glacier 
			  basins on the Peninsula (<AppLink to="https://doi.org/10.1017/S0954102014000200" target="_blank" rel="noopener" class="text-link">Cook et al., 2014</AppLink>). If you zoom in sufficiently on the Antarctic Peninsula, glacier names from the
			  <AppLink to="https://apc.antarctica.ac.uk/gazetteers/go-to-gazetteers/" target="_blank" rel="noopener" class="text-link">British Antarctic Territory gazetteer</AppLink> 
			  will be displayed. Note that all basins have been simplified for performance, so the outlines displayed are different to those available in the cited datasets.</li>
           </ul>
		   <p>
		     <strong>Analysis layers</strong>
		   </p>
		   <p>
		     The analysis layers panel allows you to display and compare all ice sheet-wide maps of ice flow in our multi-source dataset. This allows you to explore maps of ice motion
			 from any time period, as well as the long-term average maps available in the "Overview" panel. The panel also allows you to calculate and display the change in ice speed
			 between any two maps of ice motion, so you can examine how Greenland and Antarctica have sped up and slowed down in different locations over time. The slider at the bottom
			 of the panel allows you to adjust the colour scale, to maximise the visibility of patterns in your area of interest. 
		   </p>
		   <ul>
		      <li><em>Variable:</em> Choose "Speed", "Speed Trend" or "Measurement Count".</li>
			  <li><em>Data Source:</em> Select which data source to analyse. See the <AppLink to="/documentation/greenland" class="text-link">Greenland Data</AppLink> and 
			 <AppLink to="/documentation/antarctic" class="text-link">Antarctic Data</AppLink> documentation pages for details of each data source.</li>
			  <li><em>Measurement Epoch:</em> If analysing "Speed" you can choose to display a map of speed from any measurement epoch, or the long-term average from your selected data source.</li>
			  <li><em>Calculate Speed Change:</em> If analysing "Speed" you can optionally calculate and display a map of speed change compared to any other map of speed. Red areas correspond to speed-up and blue areas correspond to slow-down.</li>
		  </ul>
		  <p>
			When you click a point on the map an icon will appear showing the extraction location or region. 
			The icon will usually be a square with a point in the centre: the point shows where you clicked and the 
			square shows the region in which data were extracted. The size of this square is controlled by the 
			Advanced Options 
			(<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>) 
			"Buffer" setting. The colour of the square corresponds to the site number and will change dynamically depending on the number of points selected.
		  </p>
		   <br>
	</section>

		   
	<section id="chart-interpret">
		  <h3>6.5. Interpreting the Chart</h3>
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
	</section>
		  
		  
	<section id="output">
		  <h3>6.6. Output</h3>
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
			<em>Note: Only "Date", "Error_m_yr", "Time_separation_days", "Pixel_Count", "s_filt" and "data_source" are exported by default. 
			Other variables can be enabled for download within the Advanced Options menu, depending on whether multi-source queries are selected.</em>
		  </p>
          <ul>
            <li><strong>Date:</strong> The central date of the two images used to estimate ice speed.</li>
            <li><strong>Error_m_yr:</strong> An estimate of the global uncertainty in ice speed at this time period. Defined as the median speed over bedrock regions at that time.</li>
            <li><strong>Error_U_m_yr:</strong> An estimate of the global uncertainty in easting ice velocity at this time period. Defined as the median absolute easting ice velocity over bedrock regions at that time.</li>
            <li><strong>Error_V_m_yr:</strong> An estimate of the global uncertainty in northing ice velocity at this time period. Defined as the median absolute northing ice velocity over bedrock regions at that time.</li>
			<li><strong>Time_separation_days:</strong> The number of days between the two images used to estimate ice speed. So the first image was acquired on Date-Time_separation_days/2, and the second image on Date+Time_separation_days/2.</li>
			<li><strong>Pixel_Count:</strong> The number of valid speed estimates in the extraction location. This will be 1 if buffer=0. Pixel resolution is 200 metres, so the maximum value for e.g. a 500 m buffer is 25 (1000 x 1000 metre region = 5 x 5 pixel region).</li>
			<li><strong>s_filt:</strong> Horizontal ice surface speed in metres per year, from the time-filtered zarr store variable. If a buffer is used, the median speed within the resulted area is used.</li>
			<li><strong>s_raw:</strong> Horizontal ice surface speed in metres per year, from the raw (no time filtering) zarr store variable. If a buffer is used, the median speed within the resulted area is used.</li>
			<li><strong>u_filt:</strong> Horizontal  ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the time-filtered zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
			<li><strong>u_raw:</strong> Horizontal ice surface easting velocity in metres per year (positive in the polar stereographic eastwards direction), from the raw (no time filtering) zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
			<li><strong>v_filt:</strong> Horizontal  ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the time-filtered zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
			<li><strong>v_raw:</strong> Horizontal ice surface northing velocity in metres per year (positive in the polar stereographic northwards direction), from the raw (no time filtering) zarr store variable. If a buffer is used, the median velocity within the resulted area is used.</li>
            <li><strong>data_source:</strong> The data source label corresponding to every measurement epoch.</li>

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
    </section>
	
	
	<section id="references">
	      <h3>6.7. References</h3>
		  <blockquote class="citation-block">
				Luetzenburg, Gregor; Korsgaard, Niels J.; Deichmann, Anna K.; Socher, Tobias; Gleie, Karin; Scharffenberger, Thomas; Fahrner, Dominik; Nielsen, Eva B.; How, Penelope; Bjork, Anders A.; Kjeldsen, Kristian K.; Ahlstrom, Andreas P.; Fausto, Robert S., 2025, "PROMICE-2022 Ice Mask", https://doi.org/10.22008/FK2/O8CLRE, GEUS Dataverse, V3.
		  </blockquote>
		  <blockquote class="citation-block">
				Gerrish, L., Ireland, L., Fretwell, P., Cooper, P., & Skachkova, A. (2025). Medium resolution vector polylines of the Antarctic coastline (Version 7.11) [Data set]. NERC EDS UK Polar Data Centre. https://doi.org/10.5285/333065a9-633d-4005-ae41-fb7ae5ae7a91.
		   </blockquote>
		   <blockquote class="citation-block">
				Wallis, B.J., Hogg, A.E., Zhu, Y. and Hooper, A., 2024. Change in grounding line location on the Antarctic Peninsula measured using a tidal motion offset correlation method. The Cryosphere, 18(10), pp.4723-4742. https://doi.org/10.5194/tc-18-4723-2024.
		   </blockquote>
		   <blockquote class="citation-block">
				Howat, Ian, et al., 2022, The Reference Elevation Model of Antarctica - Mosaics, Version 2, https://doi.org/10.7910/DVN/EBW8UC, Harvard Dataverse, V1, [16/02/2026].
		   </blockquote>
		   <blockquote class="citation-block">
				Howat, I., Negrete, A. & Smith, B. (2015). MEaSUREs Greenland Ice Mapping Project (GIMP) Digital Elevation Model. (NSIDC-0645, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/NV34YUIXLP9W. [describe subset used if applicable]. Date Accessed 02-16-2026.
		   </blockquote>
		   <blockquote class="citation-block">
		        Cook AJ, Vaughan DG, Luckman AJ, Murray T. A new Antarctic Peninsula glacier basin inventory and observed area changes since the 1940s. Antarctic Science. 2014;26(6):614-624. doi:10.1017/S0954102014000200
		   </blockquote>
		   <blockquote class="citation-block">
		        Mouginot J, Rignot E (2019). Glacier catchments/basins for the Greenland Ice Sheet [Dataset]. Dryad. DOI: 10.7280/D1WT11
		   </blockquote>
		   <blockquote class="citation-block">
		        Mankoff, K.D., Noël, B., Fettweis, X., Ahlstrøm, A.P., Colgan, W., Kondo, K., Langley, K., Sugiyama, S., Van As, D. and Fausto, R.S., 2020. Greenland liquid water discharge from 1958 through 2019. Earth System Science Data, 12(4), pp.2811-2841. DOI: https://doi.org/10.5194/essd-12-2811-2020.
		   </blockquote>
		   <blockquote class="citation-block">
				Mankoff, K. D.: Freshwater runoff, GEUS Dataverse, https://doi.org/10.22008/promice/freshwater, 2020. 		   
			</blockquote>
		<br>
	</section>

  </div>
</template>



// ----- CSS ---- //
<style scoped>

/* --- ICONS --- */
.inline-icon {
  display: inline-block;
  height: 2em;       /* Scales relative to the font size (makes it fit) */
  width: 2em;         /* Maintains aspect ratio */
  vertical-align: middle; /* Aligns center of icon with center of lowercase text */
  margin: 0 0px;       /* Adds a tiny bit of breathing room */
  position: relative;  
  top: -2px;           /* visual tweak to lift it slightly if needed */
  fill: currentColor;  /* Optional: makes the icon take the text color */
}


</style>