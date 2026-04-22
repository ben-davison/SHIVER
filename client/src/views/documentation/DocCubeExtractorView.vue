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
  
    <section id="SHIVER Data Cube Extractor">
          <h1>Introduction</h1>
          <p class="intro-text">
            Welcome to the technical documentation for <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR).
            SHIVER allows you to explore and download a multitude of ice velocity measurements for Greenland and Antarctica using one simple interface.
          </p>
		  <br>
    </section>
    
    <section id="basic-usage">
		  <h3>7.1. Basic Usage</h3>
		  <p>
			The SHIVER Data Cube Extractor lets you quickly and easily extract a 'data cube' of ice velocity measurements for any time period and
			location on the Greenland and Antarctic ice sheets. Just navigate to your glacier of interest and draw a polygon or upload a shapefile and 
			select your time period and variables/data sources of interest then initiate the download. 
		  </p>
		  <p>
		    SHIVER allows you to extract data cubes from two different data sets. The "SHIFT" data set provides access to all horizontal velocity components and
			two levels of speed quality (raw and time-filtered). The SHIFT data set can be resampled to monthly, quarterly or annual resolution, on top of the 'native' 
			temporal resolution of 6- or 12-days. The "Multisource" data set allows access to numerous data sources (as well as SHIFT), but only 
			serves speed and speed error data. 
		  </p>
		  <p>
		    Your download request will be sent to the server and you will be emailed with a download link once the data cube extraction is complete.
		  </p>
		  <p>
			SHIVER allows you to extract ice velocity data cubes in Greenland or Antarctica. You can navigate to your preferred ice sheet by clicking the Greenland button 
			(<greenlandIcon class="inline-icon"/>)
			or the Antarctica button
			(<antarcticaIcon class="inline-icon"/>)
		  </p>
		  <p>
		    <strong>Data Cube limits:</strong> To reduce the load on our server, we limit individual data cube extraction volumes to a maximum of 10,000 kilometres squared
			and one year. If you require a larger data cube, then split your download into multiple requests or contact the SHIVER team via email (shiver@sheffield.ac.uk) with your request.
		  </p>
		  <br>
    </section>
		  
	<section id="file-upload">
			<h3>7.2. Uploading Files   
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
		  <br>
	</section>

	<section id="map-interpret">
          <h3>7.3. Navigating & Interpreting the Map</h3>
		  <p>
		    When you first access the SHIVER Data Cube Extractor, you will see a map of Greenland with a long-term average ice speed estimate overlain. 
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
		  
		  
	<section id="output">
		  <h3>7.4. Output</h3>
		  <p>
		    The retrieved data cubes will be in NetCDF format. 
		  </p>
		  <p><strong>NetCDF naming convention:</strong></p>
		  <ul>
			<li>SHIFT data cubes have this format: IceSheet_Frequency_StartTime_EndTime_RANDOM.nc e.g., Greenland_native_2018-01-01_2018-03-31_6b78cebb.nc. 
			Is a data cube for Greenland at the 'native' temporal resolution of the Sentinel-1 measurements from the 1st of January 2018 to the 31st of March 2018. The random suffix is to prevent overwrites from other users.</li>
			<li>Multisource data cubes have this format: IceSheet_multisource_StartTime_EndTime_RANDOM.nc e.g., Greenland_native_2018-01-01_2018-03-31_6j48egb.nc. 
			Is a data cube for Greenland from the multisource data set from the 1st of January 2018 to the 31st of March 2018.</li>
		  </ul>
		  
		  <p>
			<strong>Each SHIFT NetCDF file could contain contain:</strong>
			<br>
			<em>Note: Only "x", "y", and "time" are exported by default. 
			Other exported variables depend on the selected options. </em>
		  </p>
		  <ul>
            <li><strong>x:</strong> The easting coordinates of the grid, in the local projection.</li>
			<li><strong>y:</strong> The northing coordinates of the grid, in the local projection.</li>
			<li><strong>time:</strong> The date of the measurement. For exports at the 'native' resolution, this represents the mid-date of the measurement epoch. For exports at other temporal resolution, this will be the beginning of the averaging period.</li>
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
            <li><strong>time_separation:</strong> The number of days between the two images used to estimate ice speed. So the first image was acquired on Date-Time_separation_days/2, and the second image on Date+Time_separation_days/2.</li>
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
		  
		  <p>
			<strong>Each Mutltisource NetCDF file contains:</strong>
		  </p>
		  <ul>
            <li><strong>x:</strong> The easting coordinates of the grid, in the local projection.</li>
			<li><strong>y:</strong> The northing coordinates of the grid, in the local projection.</li>
			<li><strong>time:</strong> The date of the measurement. This represents the mid-date of the measurement epoch.</li>
            <li><strong>speed:</strong> Horizontal ice surface speed in metres per year.</li>
			<li><strong>error:</strong> Horizontal ice surface speed error in metres per year. This is as provided with each of the underlying data sources or 5% of the speed if no error is provided.</li>
			<li><strong>data_source:</strong> The name of the data source corresponding to each row in 'time' i.e. each measurement epoch in 'speed'.</li>
            <li><strong>time_separation:</strong> The number of days between the two images used to estimate ice speed. So the first image was acquired on time-time_separation/2, and the second image on time+time_separation/2.</li>
		  </ul>
		  <br>
    </section>
	
	
	<section id="references">
	      <h3>7.5. References</h3>
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