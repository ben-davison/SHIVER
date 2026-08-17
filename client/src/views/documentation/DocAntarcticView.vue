<script setup>
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import ZoomableFigure from '../../components/ZoomableFigure.vue'

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
    
    <section id="introduction">
      <h1>Antarctic Data Sources</h1>
      <p class="intro-text">
        This page provides details of all data sources contributing to our Antarctic data cube.
      </p>
    </section>

    <section id="overview">
      <h2>3.1. Data Source Overview</h2>
      <p>Our Antarctic ice speed data cube is created from seventeen individual data sources:</p>
	  <ul>
	    <li><strong>SHIFT:</strong> 12-day snapshots over the Antarctic Peninsula. 2014 to 2026.</li>
		<li><strong>ENVEO monthy:</strong> Monthly averages, Antarctic-wide. 2014 to 2021.</li>
		<li><strong>ENVEO (Pine Island):</strong> 6- and 12-day snapshots, Pine Island Glacier only. 2014 to 2019.</li>
		<li><strong>ENVEO ERS:</strong> Variable temporal resolution and various glaciers. 1992 to 1999.</li>
		<li><strong>ENVEO TSX:</strong> Variable temporal resolution, mostly Larsen-B area. 2007 to 2018.</li>
		<li><strong>ENVEO ALOS:</strong> Variable temporal resolution, mostly Larsen-B area, 2009 to 2017.</li>
		<li><strong>ENVEO TSX & Sentinel-1:</strong> Variable temporal resolution, Larsen-B area. 2015 to 2016.</li>
		<li><strong>ENVEO TSX & PALSAR:</strong> Variable temporal resolution, Larsen-B area. 2010 to 2012.</li>
		<li><strong>MEaSUREs multi-year:</strong> Multi-year averages, Antarctic-wide. 1995-2001, 2007-2009, 2014-2017, 2020-2022.</li>
		<li><strong>MEaSUREs annual:</strong> Annual (July through June) averages, Antarctic-wide. 2000 to 2025.</li>
		<li><strong>MEaSUREs (ASE):</strong> Annual (calendar year) averages of the Amundsen Sea Embayment area. 1996 to 2012.</li>
		<li><strong>ITS_LIVE annual:</strong> Annual (calendar year) averages, Antarctic-wide. 1985 to 2024.</li>
		<li><strong>ESA CCI annual:</strong> Annual (April through March) averages, Antarctic-wide. 2021 to 2023.</li>
		<li><strong>SID annual:</strong> Annual (calendar year) averages, Antarctic-wide. 2015 to 2024.</li>
		<li><strong>Joughin Sentinel-1 (Pine Island):</strong> Quarterly averages over Pine Island Glacier, 2015 to 2020.</li>
		<li><strong>Joughin TSX (Pine Island):</strong> Variable temporal resolution (typically a few months) over Pine Island Glacier. 2009 to 2015.</li>
		<li><strong>Li (Totten):</strong> Annual to multi-year averages over Totten Glacier. 1963-1973, 1973-1989 and 1989.</li>
	  </ul>
	  <p>A summary of these data sources is shown in Figure 3.1 and each of the data sources are detailed in the sections below.</p>
	  
	  <ZoomableFigure caption="Fig. 3.1: Timeseries overview of Antarctic ice speed data sources.">
			<img src="../../assets/documentation/antarctica/verification_timeline.png" alt="Data source timeline overview">
      </ZoomableFigure>
	  <br>
    </section>
	
	<section id="shift">
      <h2>3.2. SHIFT</h2>
	  <p>The SHIFT data provide 6- and 12-day snapshots of ice speed over the Antarctic Peninsula derived from feature intensity of Sentinel-1 image pairs from 2014 to 2026. 
	  The SHIFT processing pipeline is described in detail in the <AppLink to="/documentation/shift" class="text-link">SHIFT Documentation Page</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.2: Overview of the Antarctic SHIFT data.">
			<img src="../../assets/documentation/antarctica/verification_maps_SHIFT.png" alt="SHIFT data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Davison, B. J. and Sole, A. J. 2026. SHeffield Ice Flow Tracker (SHIFT) velocity data: Antarctic Peninsula ice surface velocity fields derived from intensity tracking of Sentinel-1 Synthetic Aperture Radar image pairs. [Online]. Available from: https://doi.org/10.15131/shef.data.33113111.v1
	  </blockquote>
	  <blockquote class="citation-block">
		Davison, B.J., Sole, A.J., Cowton, T.R., Lea, J.M., Slater, D.A., Fahrner, D. and Nienow, P.W., 2020. Subglacial drainage evolution modulates seasonal ice flow variability of three tidewater glaciers in southwest Greenland. Journal of Geophysical Research: Earth Surface, 125(9), p.e2019JF005492. DOI: https://doi.org/10.1029/2019JF005492.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="enveo_monthly">
      <h2>3.3. ENVEO monthly</h2>
	  <p>The ENVEO monthly data provide monthly averages of ice speed over the Antarctic margin derived from intensity and coherence tracking of Sentinel-1 
	  image pairs from 2014 to 2021. The ENVEO velocity processing pipeline is described in detail in <AppLink to="https://www.sciencedirect.com/science/article/pii/S0034425725004961" target="_blank" rel="noopener" class="text-link">Wuite et al. (2026)</AppLink>, 
	  and the mosaics can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.3: Overview of the ENVEO monthly data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_monthly.png" alt="ENVEO monthly data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Wuite, J., Nagler, T., Hetzenecker, M. and Rott, H., 2026. Ten years of polar ice velocity mapping using Copernicus Sentinel-1. Remote Sensing of Environment, 332, p.115092. DOI: https://doi.org/10.1016/j.rse.2025.115092
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="enveo_pig">
      <h2>3.4. ENVEO (Pine Island)</h2>
	  <p>The ENVEO (Pine Island) data provide 6- and 12-day snapshots of ice speed over Pine Island Glacier derived from intensity and coherence tracking of Sentinel-1 image pairs from 2014 to 2019.
	  The ENVEO velocity processing pipeline is described in detail in <AppLink to="https://www.sciencedirect.com/science/article/pii/S0034425725004961" target="_blank" rel="noopener" class="text-link">Wuite et al. (2026)</AppLink>, 
	  and the image pair data can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.4: Overview of the ENVEO Pine Island data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_Sentinel-1_PIG.png" alt="ENVEO Pine Island data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Wuite, J., Nagler, T., Hetzenecker, M. and Rott, H., 2026. Ten years of polar ice velocity mapping using Copernicus Sentinel-1. Remote Sensing of Environment, 332, p.115092. DOI: https://doi.org/10.1016/j.rse.2025.115092
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="enveo_ers">
      <h2>3.5. ENVEO ERS</h2>
	  <p>The ENVEO ERS data provide estimates of ice speed covering the Larsen-B Embayment region, Ferrigno Ice Shelf area, Rutford Ice Stream and the Amundsen Sea Embayment region of Antarctica.
      The measurements are provided at a range of temporal resolutions - ranging from 8 days to 4 months during the period from 11th January 1992 to 11th November 1999.
	  The measurements are derived from a combination of SAR interferometry and offset tracking of ERS-1 and ERS-2 imagery.
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://tc.copernicus.org/articles/5/125/2011/" target="_blank" rel="noopener" class="text-link">Rott et al. (2011)</AppLink>, and 
	  <AppLink to="https://tc.copernicus.org/articles/9/957/2015/tc-9-957-2015.html" target="_blank" rel="noopener" class="text-link">Wuite et al. (2015)</AppLink>
	  and the data can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.5: Overview of the ENVEO ERS data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_ERS.png" alt="ENVEO ERS data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Rott, H., Müller, F., Nagler, T. and Floricioiu, D., 2011. The imbalance of glaciers after disintegration of Larsen-B ice shelf, Antarctic Peninsula. The Cryosphere, 5(1), pp.125-134. DOI: https://doi.org/10.5194/tc-5-125-2011. 
	  </blockquote>
	  <blockquote class="citation-block">
		Wuite, J., Rott, H., Hetzenecker, M., Floricioiu, D., De Rydt, J., Gudmundsson, G.H., Nagler, T. and Kern, M., 2015. Evolution of surface velocities and ice discharge of Larsen B outlet glaciers from 1995 to 2013. The Cryosphere, 9(3), pp.957-969. DOI: https://doi.org/10.5194/tc-9-957-2015. 
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="enveo_tsx">
      <h2>3.6. ENVEO TSX</h2>
	  <p>The ENVEO TSX data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula.
      The measurements are provided at a range of temporal resolutions - typically 11 or 22 days - during the period from 26th June 2007 to 12th December 2016.
	  The measurements are derived from offset tracking of TerraSAR-X image pairs. 
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://tc.copernicus.org/articles/12/1273/2018/" target="_blank" rel="noopener" class="text-link">Rott et al. (2018)</AppLink>
	  and the data can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.6: Overview of the ENVEO TSX data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_TSX.png" alt="ENVEO TSX data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Rott, H., Abdel Jaber, W., Wuite, J., Scheiblauer, S., Floricioiu, D., Van Wessem, J.M., Nagler, T., Miranda, N. and Van Den Broeke, M.R., 2018. Changing pattern of ice flow and mass balance for glaciers discharging into the Larsen A and B embayments, Antarctic Peninsula, 2011 to 2016. The Cryosphere, 12(4), pp.1273-1291. DOI: https://doi.org/10.5194/tc-12-1273-2018.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="enveo_alos">
      <h2>3.7. ENVEO ALOS-PALSAR</h2>
	  <p>The ENVEO ALOS-PALSAR data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula from the 29th September 2009 to 13th November 2009
	  and the 2nd January 2011 to 17th February 2011. The measurements are derived from offset tracking of a combination of ALOS-PALSAR image pairs. 
	  The data can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.7: Overview of the ENVEO ALOS-PALSAR data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_ALOS.png" alt="ENVEO ALOS-PALSAR data overview">
      </ZoomableFigure>
	  <br>
	</section>
	
	
	<section id="enveo_tsx_s1">
      <h2>3.8. ENVEO TSX & Sentinel-1</h2>
	  <p>The ENVEO TSX & Sentinel-1 data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula from the 31st October 2015 to the 12th December 2016. 
	  The measurements are derived from offset tracking of TerraSAR-X image pairs with gaps filled using Sentinel-1 data. 
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://tc.copernicus.org/articles/12/1273/2018/" target="_blank" rel="noopener" class="text-link">Rott et al. (2018)</AppLink>
	  and the data can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.8: Overview of the ENVEO TSX & Sentinel-1 data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_TSX_Sentinel-1.png" alt="ENVEO TSX & Sentinel-1 data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Rott, H., Abdel Jaber, W., Wuite, J., Scheiblauer, S., Floricioiu, D., Van Wessem, J.M., Nagler, T., Miranda, N. and Van Den Broeke, M.R., 2018. Changing pattern of ice flow and mass balance for glaciers discharging into the Larsen A and B embayments, Antarctic Peninsula, 2011 to 2016. The Cryosphere, 12(4), pp.1273-1291. DOI: https://doi.org/10.5194/tc-12-1273-2018.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="enveo_tsx_palsar">
      <h2>3.9. ENVEO TSX & ALOS-PALSAR</h2>
	  <p>The ENVEO TSX & ALOS-PALSAR data provide estimates of ice speed covering the Larsen-B Embayment region of the Antarctic Peninsula from the 2nd July 2010 to the 10th March 2012. 
	  The measurements are derived from offset tracking of TerraSAR-X image pairs with gaps filled using ALOS-PALSAR data. 
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://tc.copernicus.org/articles/12/1273/2018/" target="_blank" rel="noopener" class="text-link">Rott et al. (2018)</AppLink>
	  and the data can be downloaded from <AppLink to="https://cryoportal.enveo.at/data/" target="_blank" rel="noopener" class="text-link">the ENVEO cryoportal</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.9: Overview of the ENVEO TSX & ALOS-PALSAR data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ENVEO_TSX_PALSAR.png" alt="ENVEO TSX & ALOS-PALSAR data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Rott, H., Abdel Jaber, W., Wuite, J., Scheiblauer, S., Floricioiu, D., Van Wessem, J.M., Nagler, T., Miranda, N. and Van Den Broeke, M.R., 2018. Changing pattern of ice flow and mass balance for glaciers discharging into the Larsen A and B embayments, Antarctic Peninsula, 2011 to 2016. The Cryosphere, 12(4), pp.1273-1291. DOI: https://doi.org/10.5194/tc-12-1273-2018.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="measures_multiyear">
      <h2>3.10. MEaSUREs multi-year</h2>
	  <p>The MEaSUREs multi-year data provide estimates of ice speed for all of Antarctica from July through June of the following multi-year periods: 1995-2001, 2007-2009, 2014-2017 and 2020-2022. 
	  The measurements are derived by applying phase analysis and speckle tracking to SAR data and by feature tracking of optical imagery from Landsat 8. 
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2022GL100141" target="_blank" rel="noopener" class="text-link">Rignot et al. (2022)</AppLink>
	  and the data can be downloaded from <AppLink to="https://nsidc.org/data/nsidc-0761/versions/1" target="_blank" rel="noopener" class="text-link">NSIDC (0761)</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.10: Overview of the MEaSUREs multi-year data.">
			<img src="../../assets/documentation/antarctica/verification_maps_MEaSUREs_multiyear.png" alt="MEaSUREs multi-year data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Rignot, E., Mouginot, J., Scheuchl, B. and Jeong, S., 2022. Changes in Antarctic ice sheet motion derived from satellite radar interferometry between 1995 and 2022. Geophysical Research Letters, 49(23), p.e2022GL100141. DOI: https://doi.org/10.1029/2022GL100141. 
	  </blockquote>
	  <blockquote class="citation-block">
		Rignot, E., Scheuchl, B., Mouginot, J. & Jeong, S. (2022). MEaSUREs Multi-year Reference Velocity Maps of the Antarctic Ice Sheet. (NSIDC-0761, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/FB851ZIZYX5O. Date Accessed 04-16-2026.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="measures_annual">
      <h2>3.11. MEaSUREs annual</h2>
	  <p>The MEaSUREs annual data provide estimates of ice speed for all of Antarctica from July through June of the following years: 2000, 2005-2025. 
	  The measurements are derived by applying phase analysis and speckle tracking to SAR data and by feature tracking of optical imagery from Landsat 8. 
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://www.mdpi.com/2072-4292/9/4/364" target="_blank" rel="noopener" class="text-link">Mouginot et al. (2017)</AppLink>
	  and the data can be downloaded from <AppLink to="https://nsidc.org/data/nsidc-0720/versions/1" target="_blank" rel="noopener" class="text-link">NSIDC (0720)</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.11: Overview of the MEaSUREs annual data.">
			<img src="../../assets/documentation/antarctica/verification_maps_MEaSUREs_annual.png" alt="MEaSUREs annual data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Mouginot, J., Rignot, E., Scheuchl, B. and Millan, R., 2017. Comprehensive annual ice sheet velocity mapping using Landsat-8, Sentinel-1, and RADARSAT-2 data. Remote Sensing, 9(4), p.364. DOI: https://doi.org/10.3390/rs9040364.
	  </blockquote>
	  <blockquote class="citation-block">
		Mouginot, J., Scheuchl, B. & Rignot, E. (2017). MEaSUREs Annual Antarctic Ice Velocity Maps. (NSIDC-0720, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/9T4EPQXTJYW9. Date Accessed 04-16-2026.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="measures_ase">
      <h2>3.12. MEaSUREs ASE</h2>
	  <p>The MEaSUREs ASE data provide annual (calendar year) estimates of ice speed for the Amundsen Sea Embayment from 1996, 2000, 2002 and 2006 to 2012. 
	  The measurements are derived from SAR interferometry on a range of platforms. 
	  The processing techniques used to derive these velocity estimates are described in
      <AppLink to="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2013GL059069" target="_blank" rel="noopener" class="text-link">Mouginot et al. (2014)</AppLink>
	  and the data can be downloaded from <AppLink to="https://nsidc.org/data/nsidc-0545/versions/1" target="_blank" rel="noopener" class="text-link">NSIDC (0545)</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.12: Overview of the MEaSUREs ASE data.">
			<img src="../../assets/documentation/antarctica/verification_maps_MEaSUREs_ASE.png" alt="MEaSUREs ASE data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Mouginot, J., Rignot, E. and Scheuchl, B., 2014. Sustained increase in ice discharge from the Amundsen Sea Embayment, West Antarctica, from 1973 to 2013. Geophysical Research Letters, 41(5), pp.1576-1584. DOI: https://doi.org/10.1002/2013GL059069. 
	  </blockquote>
	  <blockquote class="citation-block">
		Rignot, E., Mouginot, J. & Scheuchl, B. (2014). MEaSUREs InSAR-Based Ice Velocity of the Amundsen Sea Embayment, Antarctica. (NSIDC-0545, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/MEASURES/CRYOSPHERE/nsidc-0545.001. Date Accessed 04-16-2026.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="itslive_annual">
      <h2>3.13. ITS_LIVE Annual</h2>
	  <p>The ITS_LIVE annual data provide annual (calendar year) averages of ice speed over Antarctica derived from feature tracking applied to a range of satellite missions from 1985 to 2024.
	  The ITS_LIVE velocity processing pipeline is described in <AppLink to="https://tc.copernicus.org/articles/19/3517/2025/" target="_blank" rel="noopener" class="text-link">Gardner et al. (2025)</AppLink> 
	  and <AppLink to="https://essd.copernicus.org/articles/14/5111/2022/" target="_blank" rel="noopener" class="text-link">Lei et al. (2022)</AppLink> and the mosaics are available
	  to download from <AppLink to="https://nsidc.org/apps/itslive/" target="_blank" rel="noopener" class="text-link">the ITS_LIVE website</AppLink>.</p>
	  
	  <ZoomableFigure caption="Fig. 3.13: Overview of the Antarctica ITS_LIVE annual data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ITS_LIVE_annual.png" alt="ITS_LIVE annual data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Gardner, A.S., Greene, C.A., Kennedy, J.H., Fahnestock, M.A., Liukis, M., López, L.A., Lei, Y., Scambos, T.A. and Dehecq, A., 2025. ITS_LIVE global glacier velocity data in near-real time. The Cryosphere, 19(9), pp.3517-3533. DOI: https://doi.org/10.5194/tc-19-3517-2025. 
	  </blockquote>
	  <blockquote class="citation-block">
		Gardner, A. S., Fahnestock, M. & Scambos, T. (2022). MEaSUREs ITS_LIVE Regional Glacier and Ice Sheet Surface Velocities. (NSIDC-0776, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/6II6VW8LLWJ7. Date Accessed 08-17-2026. 
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="esa_annual">
      <h2>3.14. ESA CCI Annual</h2>
	  <p>The ESA CCI Annual data provide annual (April through March) averages of ice speed over Antarctica derived from Sentinel-1 image pairs acquired during 2021 to 2024.
	  The mosaics can be accessed through the 
	  <AppLink to="https://cds.climate.copernicus.eu/datasets/satellite-greenland-ice-sheet-velocity?" target="_blank" rel="noopener" class="text-link">Copernicus Climate Data Store</AppLink>.
	  </p>
	  
	  <ZoomableFigure caption="Fig. 3.14: Overview of the ESA CCI annual data.">
			<img src="../../assets/documentation/antarctica/verification_maps_ESA_CCI_annual.png" alt="ESA CCI annual data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Wuite, J., (2026): Ice sheet velocity for Antarctica and Greenland derived from satellite observations. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.0b96b838 (Accessed on 26-Apr-2026)
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="sid_annual">
      <h2>3.15. SID Annual</h2>
	  <p>The SID (Satellite Ice Dynamics) annual data provide annual (January through December) averages of ice speed over Antarctica derived from Sentinel-1 image pairs acquired during 2015 to 2025.
	  The mosaics can be accessed through the 
	  <AppLink to="https://catalogue.ceda.ac.uk/uuid/c0b464b3da9845758cd33591e57c4abf/" target="_blank" rel="noopener" class="text-link">CEDA Archive</AppLink>.
	  </p>
	  
	  <ZoomableFigure caption="Fig. 3.15: Overview of the SID annual data.">
			<img src="../../assets/documentation/antarctica/verification_maps_SID_annual.png" alt="SID annual data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Hogg, A.E.; Davison, B.J.; Rigby, R.; Wallis, B.J.; Slater, R.A.W. (2025): EOCIS: Ice Sheet Velocity, V1. NERC EDS Centre for Environmental Data Analysis, 17 April 2025. doi:10.5285/c0b464b3da9845758cd33591e57c4abf. https://dx.doi.org/10.5285/c0b464b3da9845758cd33591e57c4abf
	  </blockquote>
	  <blockquote class="citation-block">
		Davison, B.J., Hogg, A.E., Rigby, R., Veldhuijsen, S., van Wessem, J.M., van den Broeke, M.R., Holland, P.R., Selley, H.L. and Dutrieux, P., 2023. Sea level rise from West Antarctic mass loss significantly modified by large snowfall anomalies. Nature Communications, 14(1), p.1479. DOI: https://doi.org/10.1038/s41467-023-36990-3.
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="joughin_s1">
      <h2>3.16. Joughin Sentinel-1 (Pine Island)</h2>
	  <p>The Sentinel-1 quarterly averages of Pine Island Glacier ice speed are available from 1st April 2015 to the 29th September 2020.
	  These measurements are described in 
	  <AppLink to="https://www.science.org/doi/10.1126/sciadv.abg3080" target="_blank" rel="noopener" class="text-link">Joughin et al. (2021)</AppLink> 
	  and the data are available from the supplementary information of that paper.
	  </p>
	  
	  <ZoomableFigure caption="Fig. 3.16: Overview of the Joughin Sentinel-1 data over Pine Island Glacier.">
			<img src="../../assets/documentation/antarctica/verification_maps_Joughin_Sentinel-1.png" alt="Joughin Sentinel-1 Pine Island data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Joughin, I., Shapero, D., Smith, B., Dutrieux, P. and Barham, M., 2021. Ice-shelf retreat drives recent Pine Island Glacier speedup. Science Advances, 7(24), p.eabg3080. DOI: 10.1126/sciadv.abg3080. 
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="joughin_tsx">
      <h2>3.17. Joughin TSX (Pine Island)</h2>
	  <p>The TerraSAR-X velocity estimates of Pine Island Glacier ice speed are available from 15th January 2009 to 15th January 2016 (dates are approximate).
	  The time period over which the measurements were made was not provided with the data but described as a "range of several months", so we have assumed 
	  a 6-month range here.
	  These measurements are described in 
	  <AppLink to="https://www.science.org/doi/10.1126/sciadv.abg3080" target="_blank" rel="noopener" class="text-link">Joughin et al. (2021)</AppLink> 
	  and the data are available from the supplementary information of that paper.
	  </p>
	  
	  <ZoomableFigure caption="Fig. 3.17: Overview of the Joughin TerraSAR-X data over Pine Island Glacier.">
			<img src="../../assets/documentation/antarctica/verification_maps_Joughin_TSX.png" alt="Joughin TerraSAR-X Pine Island data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Joughin, I., Shapero, D., Smith, B., Dutrieux, P. and Barham, M., 2021. Ice-shelf retreat drives recent Pine Island Glacier speedup. Science Advances, 7(24), p.eabg3080. DOI: 10.1126/sciadv.abg3080. 
	  </blockquote>
	  <br>
	</section>
	
	
	<section id="li_totten">
      <h2>3.18. Li (Totten)</h2>
	  <p>These velocity estimates only cover Totten Glacier. The measurements were derived from feature tracking of ARGON and Landsat-1&4 imagery.
	  The measurements are available for the periods 1963-1973, 1973-1989 and 1989. Dates were not provided with the data so we have assumed calendar years.
	  These measurements are described in 
	  <AppLink to="https://www.nature.com/articles/s41467-023-39588-x" target="_blank" rel="noopener" class="text-link">Li et al. (2023)</AppLink>. 
	  The link to the data provided in that paper did not work at the time of writing, but the authors shared the data on request.
	  </p>
	  
	  <ZoomableFigure caption="Fig. 3.18: Overview of the Li et al. data over Totten Glacier.">
			<img src="../../assets/documentation/antarctica/verification_maps_Li_Totten.png" alt="Li et al. Totten Glacier data overview">
      </ZoomableFigure>
	  
	  <blockquote class="citation-block">
		Li, R., Cheng, Y., Chang, T., Gwyther, D.E., Forbes, M., An, L., Xia, M., Yuan, X., Qiao, G., Tong, X. and Ye, W., 2023. Satellite record reveals 1960s acceleration of Totten ice shelf in East Antarctica. Nature Communications, 14(1), p.4061. DOI: https://doi.org/10.1038/s41467-023-39588-x. 
	  </blockquote>
	  <br>
	</section>
	
	
	

  </div>
</template>