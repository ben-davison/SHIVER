<script setup>
/**
 * DOCUMENTATION VIEW
 */

// --- IMPORT LOGOS FOR FOOTER ---
// (Copied from your HomeView to ensure consistency)
import sheffieldLogo from '../assets/UOS_logo/UOSLogo_Primary_MidnightBlack_RGB.png';
import UKRILogo from '../assets/UKRI_logo/UKRI_logo.png';
import NSFLogo from '../assets/NSF_logo/NSF_Official_logo_High_Res_1200ppi.png';
import LDEOLogo from '../assets/LDEO_logo/LDEO_logo_black.png';
import StanageLogo from '../assets/Stanage_logo/Stanage_Black.png';
// Import other pretty pictures
import S1cartoon from '../assets/documentation/S1cartoon.jpg';
import S1IW from '../assets/documentation/S1IW.png';
import excelIcon from '../components/icons/excelIcon.vue';
import graphIcon from '../components/icons/graphIcon.vue';

// Imports for scrolling with hash
import { onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()

const publicPath = import.meta.env.BASE_URL;

const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId);
  if (element) {
    // 1. Get the position of the element
    const headerOffset = 100; // Adjust this if your sticky header covers the title
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.scrollY - headerOffset;

    // 2. Scroll to it smoothly
    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    });
  }
};

// Navigate to section if search bar has hash
onMounted(() => {
  // Check if the URL has a hash (e.g. #mosaics)
  if (route.hash) {
    // 1. Wait for Vue to finish rendering the DOM
    nextTick(() => {
      // 2. (Optional) Add a tiny delay to account for any layout shifts/animations
      setTimeout(() => {
        const element = document.getElementById(route.hash.slice(1)) // Remove the '#'
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' })
        }
      }, 100) // 100ms delay is usually plenty
    })
  }
})


</script>

<template>
  <div class="doc-page">
    
    <div class="doc-container">
      
      <aside class="doc-sidebar">
        <nav>
          <h3>Contents</h3>
          <ul>
            <li><a href="#" @click.prevent="scrollToSection('introduction')">Introduction</a></li>
			<li><a href="#" @click.prevent="scrollToSection('overview')">1. Overview</a></li>
			<li><a href="#" @click.prevent="scrollToSection('data-sources')">2. Data Sources</a></li>
			<li><a href="#" @click.prevent="scrollToSection('pre-processing')">3. Pre-processing</a></li>
			<li><a href="#" @click.prevent="scrollToSection('algorithms')">4. Measurement Algorithms</a></li>
			<li><a href="#" @click.prevent="scrollToSection('post-processing')">5. Post-processing</a></li>
			<li><a href="#" @click.prevent="scrollToSection('mosaics')">6. Mosaics</a></li>
			<li><a href="#" @click.prevent="scrollToSection('automation')">7. Automation</a></li>
			<li><a href="#" @click.prevent="scrollToSection('how-to-use-timeseries')">8. SHIVER Timeseries Explorer</a></li>
			<li><a href="#" @click.prevent="scrollToSection('how-to-use-datacube')">9. SHIVER Data Cube Extractor</a></li>
			<li><a href="#" @click.prevent="scrollToSection('citation')">10. Citation & License</a></li>
          </ul>
        </nav>
      </aside>

      <main class="doc-content">
        
        <section id="introduction">
          <h1>Introduction</h1>
          <p class="intro-text">
            Welcome to the technical documentation for <strong>SHIFT</strong> (SHeffield Ice Flow Tracker)
            and <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR). This platform provides access to high-resolution ice velocity time-series data 
			derived from Sentinel-1 Synthetic Aperture Radar (SAR) imagery.
          </p>
        </section>

        <section id="overview">
          <h2>1. Overview of approach</h2>
          <p>
            The velocity fields are derived using <a href="#" @click.prevent="scrollToSection('algorithms')">intensity tracking algorithms</a> applied to consecutive 
			<AppLink to="https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1" target="_blank" rel="noopener" class="text-link">Sentinel-1</AppLink>
			image pairs. Our processing pipeline is fully automated and involves:
          </p>
          <ul>
            <li><strong>Metadata curation and data download:</strong> At least daily, our system collates information about all Sentinel-1 images that have 
			been acquired over Greenland and Antarctica and identifies all potential image pairs. For each available image pair that hasn't yet been processed,
			it downloads the images, orbital positioning information and digitial elevation models required to complete the processing. All data download and curation 
			is completed 'on-the-fly' to minimise storage requirements.</li>
            <li><strong>Pre-processing:</strong> We use the open-source Generic Mapping Tools for Synthetic Aperture Radar 
			<AppLink to="https://topex.ucsd.edu/gmtsar/" target="_blank" rel="noopener" class="text-link">(GMTSAR)</AppLink> imagery software 
			to prepare the raw radar images for feature tracking and generate the information required to convert the images from radar to map coordinates. 
			This process ingests the raw radar images, orbital data and elevation data.</li>
            <li><strong>Feature/intensity/speckle tracking:</strong> 2D fields of ice velocity are estimated and posted at 150x150 m resolution using 
			<a href="#" @click.prevent="scrollToSection('algorithms')">standard methods</a>.</li>
			<li><strong>Post-processing:</strong> Individual velocity fields are filtered to remove outliers, which are defined using cross-correlation quality metrics and 
			based on the characteristics of the retrieved flow field.</li>
			<li><strong>Mosaic creation:</strong> The 'raw' velocity fields derived from Sentinel-1 swaths are geocoded to a common grid and further corrections 
			and outlier removal routines are applied.</li>
          </ul>
        </section>


        <section id="data-sources">
          <h2>2. Data Sources</h2>
          <p>
            <strong>Sentinel-1:</strong> The 
			<AppLink to="https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1" target="_blank" rel="noopener" class="text-link">European Space Agency (ESA) Sentinel-1 missions</AppLink>
			 comprise a constellation of two sun-synchronous polar-orbiting satellites,
			which operate  in the same orbital plane with 180 degree phasing difference. They perform C-band Synthetic Aperture Radar (SAR) imaging, enabling day and night 
			acquisitions regardless of weather. 
		   </p>
			
			<figure style="text-align: center; margin: 20px 0;">
			 <img src="../assets/documentation/S1cartoon.jpg" alt="Sentinel-1 radar vision" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
			 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
			   Fig. 2.1: Artistic impression of Sentinel-1 image acquisition. Credit: ESA/ATG medialab.
			 </figcaption>
		  </figure>
		  			
			<div class="info-box">
			  <p>
				<strong>What is a radar image?</strong> 
				Radar imaging is an "active" data collection technique where the satellite radar transmits its own pulses of energy and records the amount reflected back 
				from the Earth's surface - surfaces that reflect more energy back appear brighter. Typically, rougher surfaces and surfaces oriented towards the incoming radar waves 
				appear brighter than smooth surfaces or those that are facing away from the sensor. Surface properties also affect how much of the incoming radar signal is returned to the
				satellite: crucially for glaciers, a smooth wet surface (as might be expected on glaciers during summer), acts as a 'specular reflector', which causes the radar waves to
				reflect away from the satellite and makes water appear dark in radar imagery. 
				This all differs from optical imagery, which relies on passive light from the sun.
				<br><br>
			  </p>
			  
			  <figure style="margin: 0; text-align: center;">
				<video 
				  class="box-image"
				  autoplay 
				  loop 
				  muted 
				  playsinline
				>
				<source 
					  :src="`${publicPath}videos/Wilkinson_Murphy_Glacier_BM3D_gif_8fpf_150dpi.mp4`" 
					  type="video/mp4"
				>
				  Your browser does not support the video tag.
				</video>
				<figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
				  Fig. 2.2: A Sentinel-1 radar image animation, showing the retreat of Wilkinson Murphy Glacier, Antarctica. Contains modified Copernicus Sentinel data.
				</figcaption>
			  </figure>
			  <p>
				For our processing with SHIFT, we use Sentinel-1 Level-1 Single Look Complex (SLC) images. SLC images represent the 'raw' radar returns from the ground surface,
				processed into a 2D image, but before those radar returns have been projected onto the ground surface. Since it has not been projected, the raw SLC image is in 
				'slant range' or 'line-of-sight' geometry, as if you are viewing the surface from the perspective of the satellite antenna without knowing anything about the 
				ground topography. As part of our processing, we also produce ground-projected radar amplitude images (as shown in Fig. 2.2).
			  </p>
			</div>
			
			
		 <p>
			Sentinel-1A was launched on 3 April 2014, Sentinel-1B was launched on 25 April 2016, Sentinel-1C was launched on 5 December 2024 and Sentinel-1D was 
			launched on 4 November 2025. Sentinel-1B experienced a 
			<AppLink to="https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Mission_ends_for_Copernicus_Sentinel-1B_satellite" target="_blank" rel="noopener" class="text-link">failure of the power supply</AppLink>.
			on 23 December 2021, leaving it unable to deliver images.
			<br><br>
			Each of these individual satellites orbits the Earth in a consistent pattern. This allows them to image the same location on the ground every 12-days (so-called 'repeat' imagery). 
			Since each pair of satellites orbit the Earth 180 degrees apart but in the same orbital plane, we can combine the images from pairs of Sentinel-1 satellites to acquire repeat
			images every six days. Since our ice velocity measurements require us to measure the movement of surface features over some time period, this repeat image acquisition time
			period means that our velocity measurements represent the average ice speed during the time period between image acquisitions (which must be a multiple of six days).
					
			The Sentinel-1 SAR instrument can acquire images in 
		    <AppLink to="https://sentiwiki.copernicus.eu/web/s1-products" target="_blank" rel="noopener" class="text-link">four exclusive modes</AppLink>:
		</p>
		   <ul>
              <li><strong>Stripmap:</strong> the standard mode.</li>
              <li><strong>Interferometric Wide (IW) swath:</strong> where three 'swaths' of data are acquired using the <AppLink to="https://ieeexplore.ieee.org/document/1677745" target="_blank" rel="noopener" class="text-link">TOPSAR</AppLink> technique.</li>
              <li><strong>Extra Wide swath:</strong> where five 'swaths' of data are acquired using the TOPSAR technique, but at lower resolution to the IW mode.</li>
			  <li><strong>Wave:</strong> where small 'vignettes' of data are acquired at 100 km along-track intervals, alternating between near- and far-range incidence angles.</li>
          </ul>
		  
		  <p>
			For our processing with SHIFT, we use images acquired in Interferometric Wide swath mode.
		  </p>
		  
		  <figure style="text-align: center; margin: 20px 0;">
			 <img src="../assets/documentation/S1IW.png" alt="Sentinel-1 IW acquisition geometry" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
			 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
			   Fig. 2.3: The acquisition geometry of Sentinel-1 IW images.
			 </figcaption>
		  </figure>
		  
		  <div class="info-box">
			 <p>
               <strong>What is Synthetic Aperture Radar (SAR)?</strong> 
			   Synthetic Aperture Radar (SAR) is a way of acquiring radar images that increases their spatial resolution.
			   The resolution of a radar imaging system depends, among other things, on the length of the antenna - longer antennas provide higher resolutions and therefore more detailed imagery. 
			   To achieve high-resolution images (meaning images with pixel dimensions of several metres) from space, a standard radar would require an impractically large antenna 
			   (over 4,000 meters long for C-band radar!). 
			   SAR solves this by using the motion of the satellite to simulate a much larger antenna. By combining a sequence of signals received as the satellite moves along its flight 
			   path, it creates a "synthetic aperture" that produces high-resolution data from a physically small antenna.
			   You can read more about SAR <AppLink to="https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar" target="_blank" rel="noopener" class="text-link">here</AppLink>.
             </p>
			</div>
			
			<p>
				Sentinel-1 Single Look Complex (SLC) data are provided in various polarisation, but HH (horizontal emit and horizontal receive) is best for ice velocity estimation. 
			</p>
		
          
        </section>
		
		
		<section id="pre-processing">
          <h2>3. Pre-processing</h2>
          <p>
            We use <AppLink to="https://topex.ucsd.edu/gmtsar/" target="_blank" rel="noopener" class="text-link">GMTSAR</AppLink> to convert Sentinel-1 SLC IW 
			image pairs to co-registered, geocoded amplitude images suitable for feature tracking. In the following, the first and second image in the image pair is referred to as image1
			and image2, respectively.
		  </p>
			<ul>
              <li><strong>Geometric alignment, deramping and burst stitching:</strong> We use information about the satellite position and the ground surface to align image2
					  with image1. Deramping removes the phase ramp inherent in TOPS (Terrain Observation with Progressive Scans) data, resulting from the steering of the antenna
					  beam during acquisition, to ensure phase continuity. Two levels of 
					  <AppLink to="https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html" target="_blank" rel="noopener" class="text-link">orbital information</AppLink> 
					  are available: 'Precise' and 'Restituted'  orbits. Precise orbits are accurate to 5 cm but are only available 21 days after image acquisition. Restituted orbits are 
					  accurate to 10 cm and are available within 3 hours of image acquisition. Wherever possible, we use the precise orbits. In practice, the choice of orbit information has
					  no discernable impact on the retrieved velocity field. We then stitch bursts together to form three sub-swaths per image pair. We use a fixed map of the ice surface
					  provided by Digitial Elevation Models (DEMs). For the Antarctic Peninsula, we use the 100 m REMA DEM mosaic, whilst for Greenland we use the 90 m Greenland Ice Mapping Project DEM.</li>
					  
              <li><strong>Geocoding of amplitude:</strong> Once the complex images are prepared, we extract the amplitude component. Then we calculate a transformation function 
			          between radar coordinates and geographic coordinates, accounting for elevation and time. We retain the image in radar coordinates until after the feature tracking is complete.</li>
          </ul>     
		<p>
            Prior to feature tracking, we apply a Contrast-Limited Adaptive Histogram Equalization filter to the pre-prepared amplitude images to maximize the visibility of surface features. 
		  </p>
        </section>
		
		
		<section id="algorithms">
          <h2>4. Measurement Algorithms</h2>
          <p>
			Our core processing pipeline is adapted from, 
			(<AppLink to="https://uk.mathworks.com/matlabcentral/fileexchange/45028-pivsuite" target="_blank"><strong>PIVSuite</strong></AppLink>)
			which was inspired by
			(<AppLink to="https://openresearchsoftware.metajnl.com/articles/10.5334/jors.334" target="_blank">PIVLab</AppLink>). 
			We use fairly standard "feature tracking" approaches to measure the displacement of ice surface features between two co-registered SAR images.
		  </p>

		  <h3>4.1. Interrogation Areas (IAs)</h3>
		  <p>
			Feature tracking does not track every individual ground feature. Instead, the image1 and image2 are divided into small sub-images called <strong>Interrogation Areas (IAs)</strong>.
		  </p>
		  
		  <figure style="text-align: center; margin: 20px 0;">
			 <img src="../assets/documentation/IAs.png" alt="Grid of Interrogation Areas" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
			 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
			   Fig. 4.1: Concept of splitting the images into Interrogation Areas.
			 </figcaption>
		  </figure>

		  <div class="info-box">
			<strong>Concept:</strong> Imagine cutting a small square (the IA) out of the first image and sliding it over the second image until the patterns inside the square match perfectly. The distance you moved the square is the ice displacement vector.
		  </div>

		  <p>
			The size and distribution of these IAs are critical tunable parameters:
		  </p>
		  <ul>
			<li>
			  <strong>IA Size:</strong> The window size (e.g., 64x64 or 128x128 pixels). 
			  Larger IAs contain more distinct features, typically providing a stronger correlation signal, but they effectively "average" the velocity over a larger area. 
			  Smaller IAs measure displacement over smaller areas, but are more susceptible to noise or "loss of correlation". Since Sentinel-1 images have different
			  resolutions in the range (line-of-sight) and azimuth (along-flight or along-track) directions (nominally 2.3 x 14.1 m), we use different IA lengths in each direction. 
			  In general, it is recommended that the dimensions of the IA should be at least four times the maximum expected displacement.
			</li>
			<li>
			  <strong>Step Size (Overlap):</strong> To produce a smooth velocity map, IAs can (and should!) overlap. 
			  For example, if the IA size is 128 pixels, we might step the grid by only 32 pixels. 
			  This produces a dense grid of velocity vectors. Typically, the step will be 25% or less of the IA size; we use a step of 12.5% of the IA dimensions.
			  <em>Note: Higher overlap increases the computational cost linearly with the number of generated IAs.</em>
			</li>
		  </ul>

		  <h3>4.2. Frequency Domain Cross-Correlation</h3>
		  <p>
			Calculating the correlation by physically sliding the IA over the search area (Spatial Cross-Correlation) is computationally expensive, with a complexity of <em>O(N<sup>2</sup>)</em>. 
			Instead, we perform <strong>Circular Cross-Correlation</strong> in the frequency domain using the Fast Fourier Transform (FFT).
		  </p>
		  
		  <p>
			According to the Convolution Theorem, the cross-correlation of two functions is equivalent to the multiplication of their Fourier Transforms. 
			For each IA pair, we calculate the 2D cross-correlation surface (<em>R<sub>corr</sub></em>) as:
		  </p>

		  <div class="citation-block" style="text-align: center; margin: 20px 0; font-family: 'Times New Roman', serif; font-size: 1.3rem;">
			<em>R<sub>corr</sub></em> = 
			<strong>F</strong><sup>-1</sup> 
			( <strong>F</strong>(<em>IA<sub>1</sub></em>) &cdot; <strong>F</strong>(<em>IA<sub>2</sub></em>)<sup>*</sup> )
		  </div>

		  <p>
			Where <strong>F</strong> denotes the Fourier Transform and <sup>*</sup> denotes the complex conjugate. 
			Before transformation, windowing functions (e.g., Hanning, Gaussian) are applied to the IAs to reduce spectral leakage caused by edge discontinuities.
		  </p>
		  
		  <p>
			The result is a 2D surface of the magnitude of the correlation strength between image1 and image2, depending on the displacement applied to image1. The correlation at any
			<em>(x,y)</em> location within the 2D surface can be between -1 and 1. The largest value - <em>the signal</em> - is where the correlation between the two IAs is greatest,
			so the distance between the centre of the IA to the centre of the cross-correlation peak should correspond to the average displacement between image1 and image2. The 
			mean of the absolute values of the remainder of the 2D cross-correlation surface is referred to as the <em>noise</em>. Therefore, the ratio of the cross-correlation
			peak magnitude and the noise is called the <em>signal-to-noise ratio</em> or SNR. Low SNR values indicate low confidence (e.g., in areas of featureless snow), 
			allowing us to filter out bad data during post-processing.
		  </p>
		  <p>
			<em> Note: In reality, there may be spatial variations of ice speed within the IA. These are not resolved. </em>
		  </p>
			
			<figure style="text-align: center; margin: 20px 0;">
			 <img src="../assets/documentation/CC.jpg" alt="2D cross-correlation field" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
			 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
			   Fig. 4.2: A 2-D cross-correlation field for a single IA.
			 </figcaption>
		  </figure>

		  <h3>4.3. Sub-Pixel Peak Finding</h3>
		  <p>
			Integer-level precision is insufficient for measuring ice motion. To illustrate, imagine the true displacement over a 6-day period is 1.25 pixels in the range direction, 
			where each pixel is 2.3 m in that direction (so 2.875 m of displacement). That is equivalent to a speed of 175 m/yr. Now imagine we only measured the location of the 
			cross-correlation peak to the nearest pixel. That would give 1 pixel or 2.3 m of displacement, which is 140 m/yr and a 20% error! The error is greater in the azimuth
			direction because the pixel sizes are larger, but lower over 12-day periods because the error per day is less.
		  </p>
		  <p>
			To achieve sub-pixel accuracy, we implement the <strong>matrix-multiply DFT approach</strong> described by 
			<AppLink to="https://opg.optica.org/ol/fulltext.cfm?uri=ol-33-2-156" target="_blank">Guizar-Sicairos et al. (2008)</AppLink>.
		  </p>
		  <p>
			Rather than zero-padding the entire FFT (which is memory intensive), this algorithm computes the discrete Fourier transform (DFT) only in a small neighborhood around the initial integer peak. 
			This effectively "zooms in" on the peak in the frequency domain, allowing us to locate the maximum with precision of 1/50th of a pixel, with minimal computational overhead.
		  </p>

		  <h3>4.4. Advanced Refinements</h3>
		  <p>
			To tackle areas of complex ice flow or areas with particularly low signal-to-noise ratio, our workflow supports advanced iterative methods:
		  </p>
		  <ul>
			<li><strong>Multi-pass Processing:</strong> We perform an initial coarse tracking pass. The resulting velocity estimates are used to pre-shift the IAs for a second, finer pass. This compensates for large displacements and improves correlation.</li>
			<li><strong>Iterative Shifting & Noise Injection:</strong> To prevent "pixel locking" (where velocities bias toward integer values), we can iteratively shift the IA position slightly or inject low-level noise, averaging the results to smooth out quantization errors.</li>
		  </ul>
        </section>


		<section id="post-processing">
          <h2>5. Post-processing</h2>
			  <p>
				Raw velocity fields derived from feature tracking inevitably contain noise and artifacts caused by ionospheric streaks, featureless surfaces (like fresh snow), or decorrelation. Our post-processing pipeline cleans this data in three distinct stages.
			  </p>

			  <h3>5.1. Stage 1: Segmentation Filtering (Radar Geometry)</h3>
			  <p>
				Before geocoding, we apply an image segmentation filter based on the premise that real ice flow is usually smoothly varying. While velocity can change, "islands" of flow surrounded by areas of extremely high strain (rapid changes in speed) are typically erroneous.
			  </p>
			  <p>
				We utilize a <strong>Region Growing</strong> algorithm to identify regions of unphysically rapid velocity change surrounding relatively small groups of pixels. 
				This allows us to identify and remove small groups of pixels separated from the main velocity field by a sharp discontinuity (a 'cliff' in velocity values). The effect of 
				this is to retain a smoothly varying velocity field comprised mostly of large contiguous pixel groups whilst retaining realitic areas of steep speed gradients (such as 
				ice falls and shear margins). This approach adapts the segmentation method described by 
				<AppLink to="https://www.mdpi.com/2072-4292/9/10/1062" target="_blank">Luttig et al. (2017)</AppLink>.
			   </p>
				
				<figure style="text-align: center; margin: 20px 0;">
					 <img src="../assets/documentation/segfilt_crop.png" alt="Adapted version of Figure 5 from Luttig et al. 2017" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
					 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
					   Fig. 5.1: An illustration of the segmentation filter removing groups of outliers from the left image to produce the righthand image. Adapted from Luttig et al. (2017) Figure 5.
					 </figcaption>
				</figure>
			  

			  <h3>5.2. Stage 2: Ionospheric Destriping</h3>
			  <p>
				Velocity fields derived from Synthetic Aperture Radar data often suffer from 'striping' artifacts caused by ionospheric irregularities interfering with the radar signal. 
			  </p>
			  
			  <p>
				We conditonally apply a general destriping algorithm described by 
				<AppLink to="https://opg.optica.org/oe/fulltext.cfm?uri=oe-33-3-5800" target="_blank">Rottmayer et al. (2025)</AppLink>. 
			  </p>
			  <div class="info-box">
				<strong>Conditional Application:</strong> 
				Not all velocity fields contain stripes and attempts to destripe do not always reduce apparent striping in the retrieved 
				velocities - results depend on the initial quality of the velocity field. Therefore, our pipeline calculates noise metrics 
				(using BRISQUE and other noise estimation functions) <em>before</em> and <em>after</em> the destriping filter runs. 
				The destriped result is only accepted if the algorithm detects a quantifiable reduction in noise levels. This is necessary
				in part because stripes can only be clearly detected (and removed) if the velocity field is relatively complete - large gaps
				or significant noise from other sources can hinder stripe detection.
			  </div>
			  
			  <figure style="text-align: center; margin: 20px 0;">
					 <img src="../assets/documentation/destripe.png" alt="Example destriping" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
					 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
					   Fig. 5.2: An illustration of striping in a velocity field and the effect of stripe removal. Note the difference in colour scale range of the right-hand panel.
					 </figcaption>
			  </figure>

			  <h3>5.3. Stage 3: Map Projection & Outlier Removal</h3>
			  <p>
				Once the data are cleaned in radar coordinates, they are projected onto the ground surface map geometry. 
				This converts displacements from "pixels" into "meters" and corrects for topographic distortion.
			  </p>
			  <p>
				We then run a final suite of physical and statistical filters, always attempting to remove outliers whilst minimising loss of 'good' data:
			  </p>

			  <ul>
				<li>
				  <strong>Signal-to-Noise Ratio (SNR):</strong> 
				  We reject any vectors where the cross-correlation peak strength is low relative to the noise floor. We utilize a threshold of <strong>SNR > 5.8</strong>, 
				  (i.e. velocity estimates with an SNR of less than 5.8 are removed). This threshold was established as a robust cutoff for feature tracking by 
				  <AppLink to="https://ieeexplore.ieee.org/document/4261046" target="_blank">de Lange et al. (2007)</AppLink>.
				</li>
				<li>
				  <strong>Flow Direction Filter:</strong> 
				  Vectors indicating physically impossible flow direction changes (e.g., a sudden reversal in direction) are removed.
				</li>
				<li>
				  <strong>Grubbs Outlier Detection:</strong> 
				  A statistical test that identifies and removes values that deviate significantly from the local mean (spatial outliers).
				</li>
				<li>
				  <strong>Spatial Isolation:</strong> 
				  Any remaining vectors that are completely isolated (lacking neighbors) are removed as probable noise.
				</li>
			  </ul>

			  <p>
				Finally, small gaps in the remaining velocity field are filled by solving the Dirichlet boundary value problem for the discrete 
				Laplacian over the region of the gap. In the resulting filled area, each filled pixel equals the average of its four immediate neighbours.
				This produces a smooth interpolation that preserved local flow gradients, rather than introducing artificial flat spots.
			  </p>
        </section>
		
		
		<section id="mosaics">
          <h2>6. Mosaics</h2>
			  <p>
				The processing steps described so far operate on individual Sentinel-1 image pairs, each comprised of three 'swaths'. 
				A single acquisition date pair (e.g., June 20 to June 26) may consist of multiple image pairs.
			  </p>
			  <p>
				While these swaths share the same map projection, they exist on different pixel grids based on the satellite's specific track. 
				To create an analysis-ready product, we must standardize all these swath-based velocity fields onto a common grid. 
				We achieve this by generating <strong>date-pair Mosaics</strong>.
			  </p>

			  <h3>6.1. "Raw" Mosaics</h3>
			  <p>
				The "Raw" mosaic process aggregates all velocity data derived from any Sentinel-1 pair covering the same time window 
				(e.g., all data measuring displacement between Date A and Date B). It also removes offsets in velocity estimates between
				overlapping swaths and removed biases detected in bedrock areas (where zero motion is expected, but not always measured).
			  </p>
			  
			  <h4>Step 1: Common Grid Projection</h4>
			  <p>
				We define a master 'Common Grid' that covers the entire study area (e.g., the full Antarctic Peninsula or West Greenland). 
				Using <strong>GDAL</strong> (Geospatial Data Abstraction Library) tools, every individual swath is geocoded  
				onto this fixed grid. This ensures that a pixel at index <em>(x, y)</em> in one mosaic corresponds exactly to the same 
				geographic location in every other mosaic in the time series. This grid was defined based on the maximum extent of all 
				available Sentinel-1 image pairs in the two study areas.
			  </p>

			  <h4>Step 2: Merging and Overlap Correction</h4>
			  <p>
				Sentinel-1 swaths acquired as part of the same image pair overlap. During the mosaicking process, we correct for detected
				offsets between overlapping swaths if the velocity field is of sufficient quality and the calculated offset is succiently clear.
				All applied swath offsets are 'tied' to swaths that overlap with bedrock areas.
			  </p>
			  <ul>
				<li><strong>Swath Stitching:</strong> Adjacent swaths (from the same image pair) are stitched together.</li>
				<li><strong>Image Pair Merging:</strong> If multiple image pairs were acquired on the same day, they are merged. These may or may not overlap.</li>
			  </ul>

			  <section id="error">
			  <h4>Step 3: Error and bias correction</h4>
			  <p>
				Errors in the resulting velocity fields may stem from errors in the calculated satellite position, errors caused by ionospheric interference with the 
				radar wave, errors in the DEM used for projection of the radar image and conversion of displacement field to metres, errors in image co-registration, 
				uncertainties associated with calculation of ice motion over 2D IAs, uncertainties in the calculation of the cross-correlation peak location. These errors
				are hard to quantify on a pixel-by-pixel basis. 
			  </p>
			  <p>
				To obtain a measure of the error in our velocity estimates we use two metrics. The first is simply the SNR of the cross-correlation field for each IA,
				which we also produce date-pair mosaics of. The second is the apparent deviation from zero motion across bedrock areas in velocity fields containing
				bedrock. In west Greenland, large areas of bedrock are available. Less is available on the Antarctic Peninsula. When forming the mosaics, we 
				calculate the median velocity of bedrock areas and apply that as a bias correction to the mosaics and we retain that motion as a measure of the 
				'global' error in each date-pair mosaic.
			  </p>
			  </section>

			  <h4>Step 4: Spatial Filtering</h4>
			  <p>
				Once merged and bias-corrected, we apply a <strong>Hybrid Median Filter</strong> to the mosaic. This filter is specifically chosen because it effectively 
				removes "salt-and-pepper" noise (random, high-frequency outliers) in the data, while preserving sharp edges - crucial for maintaining the distinct 
				boundaries of shear margins in ice streams. We then fill small spatial gaps in each mosaic.
			  </p>

			  <p>
				The result of this process is the <strong>raw date-pair mosaic</strong>: a spatially continuous, calibrated velocity map on a standardized grid. 
				In the interactive map, this level of data quality is referred to as 'raw' - as you can see from the above processing steps, many filters using spatial 
				information have been applied, but no time-filtering has been applied.
			  </p>
			  
				<figure style="text-align: center; margin: 20px 0;">
					 <img src="../assets/documentation/mosaicRaw.png" alt="A raw date-pair mosaic destriping" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
					 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
					   Fig. 6.1: A 'raw' date-pair mosaic over the Antarctic Peninsula in June 2020.
					 </figcaption>
			  </figure>
			  
			  <h3>6.2. Time-Filtered Mosaics ("Analysis Ready" Data)</h3>
			  <p>
				While the "Raw" mosaics provide a spatially continuous view for specific date pairs, we further reduce noise by using time-series information in each spatial cell.
				In the interactive map, this level of data quality is referred to as 'filt' - it has had outliers removed using both spatial and temporal information.
			  </p>
			  <p>
				To produce our final 'analysis-ready' product, we exploit the high temporal frequency of Sentinel-1. By stacking every available mosaic into a 3D cube 
				(Dimensions: <em>x, y, time</em>), we can analyze the history of every single pixel. This allows us to differentiate between 
				<strong>transient noise</strong> (random spikes) and <strong>real geophysical signals</strong> (such as seasonal speedups or glacial surges).
			  </p>
			  
			  <p>
				We apply three distinct filters in the temporal domain:
			  </p>

			  <h4>1. Velocity Magnitude Outlier Detection</h4>
			  <p>
				This filter examines the speed at a single pixel location over the entire record. It identifies and removes data points where the velocity deviates 
				statistically from the local temporal trend.
			  </p>
			  <ul>
				<li>
				  <strong>Method:</strong> We utilize MATLAB's <code>isoutlier</code> function. Depending on the specific region dynamics, we apply 
				  either a <strong>Hampel Filter</strong> (moving median) or a standard <strong>Median Absolute Deviation (MAD)</strong> test.
				</li>
				<li>
				  <strong>Why it works:</strong> A sudden, single-date spike in velocity of 500% is physically implausible for a glacier. However, the use 
				  of a moving window (Hampel) ensures that gradual changes (like a summer speedup or the onset of a surge) are preserved as valid data.
				</li>
			  </ul>

			  <h4>2. Velocity Gradient Filter (Texture Consistency)</h4>
			  <p>
				Sometimes, an entire scene may be contaminated by noise that produces velocity values within a "plausible" range, but with an unrealistic 
				spatial texture (e.g., "bumpy" or "jagged" flow) that deviates significantly from the historical mean spatial variations in ice flow. 
			  </p>
			  <p>
				This filter calculates the spatial gradient (numerical derivative) of the velocity field for every time step. If the spatial gradient of the 
				flow on a specific date is significantly higher than the historical median for that location, the data point is flagged as an outlier. 
				This effectively removes areas where spatial gradients in flow have changed unrealistically.
			  </p>

			  <h4>3. Flow Direction Stability</h4>
			  <p>
				Ice flow direction is generally constrained by topography and is usually expected to change little or only fairly slowly within the contraints of the imaging platform. 
				We calculate the long-term average flow direction for every pixel. We compare the flow direction of each individual date pair against this long-term average.
				If the flow direction deviates beyond a physical threshold (indicating sudden and/or unsustained change in flow direction), the velocity estimate
				in that x,y,time location is removed.
			  </p>

			  <div class="info-box">
				<strong>Result:</strong> The final output is a dense, robust time series of ice velocity that retains high-frequency real-world events while suppressing observational noise.
				Note that we retain the 'raw' mosaics, so we can adapt the temporal filtering as needed. As new image pairs are acquired and new date-pair mosaics are generated,
				we append them to the raw mosaic stack and re-filter the full time-series every time. 
				<br><br>
				The resulting 'stack' of timefiltered, analysis-ready velocity variables are stored as a cloud-optimised, chunked zarr-store, to accelerate 
				subsequent extraction, analysis and visualisation.
			  </div>
			  
			  <figure style="text-align: center; margin: 20px 0;">
					 <img src="../assets/documentation/raw_vs_timefiltered.png" alt="Ice speed timeseries" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
					 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
					   Fig. 6.2: An ice speed timeseries from Greenland comparing the 'raw' and 'timefiltered' mosaic values in one location.
					 </figcaption>
			  </figure>

        </section>
		
		
		<section id="automation">
          <h2>7. Automation</h2>
		  <p>
			Our processing is automated and powered by the University of Sheffield High Performance Cluster 
			<AppLink to="https://docs.hpc.shef.ac.uk/en/latest/stanage/" target="_blank"><strong>Stanage</strong></AppLink>.
		  </p>
		  <p>
			Our complete automation workflow is available in the document below. Much of it is specific to the University of Sheffield
            HPC cluster, so you won't be able to directly adopt our approach, but we have included it below to outline our approach.
          </p>
		  <p>
		   We use a SpatioTemporal Asset Catalog (STAC)-like architecture
			that defines all available image pairs and their processing status. This STAC is updated at least daily with new images as Sentinel-1
			acquires them and as new image pairs are processed by our in-house HPC cluster. The beauty of the STAC is that it allows us to 
			query our full catalogue of velocity swaths (or potential but unprocessed swaths) using any combination of spatial and temporal 
			filtering. It also allows us to record useful processing metadata, such as the progress through each processing stage, the number of 
			processing attempts, and the computing resources (time, RAM, #cores) required to complete each processing stage, which allows us to 
			optimise our resource requests and maximise the 'churn' of image pairs that we can process. 
		  </p>
		  <p>
		    Plus, each day we get a nice new .pdf summarising our processing progress and visualising the latest swaths that have been completed.
		  </p>
		  <div class="pdf-container">
			<object 
			  :data="`${publicPath}pdfs/SCADI_UserGuide.pdf`"
			  type="application/pdf" 
			  width="100%" 
			  height="800px"
			>
			  <div style="padding: 20px; text-align: center;">
				<p>It appears you don't have a PDF plugin for this browser.</p>
				<a :href="`${publicPath}pdfs/SCADI_UserGuide.pdf`" class="btn-download">
				  Click here to download the User Guide
				</a>
			  </div>
			</object>
		  </div>
        </section>
		
		
        <section id="how-to-use-timeseries">
		  <h2>8. SHIVER Timeseries Explorer</h2>
		  <h3>8.1. Basic Usage</h3>
          <p>
		    The SHIVER Timeseries Explorer lets you quickly and easily visualize  and export ice velocity timeseries
			anywhere we have data. To visualize the data, 
            click anywhere on the map or upload a shapefile containing a point or points to view 
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
		  
          <h3>8.2. Uploading Files   
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
		  
		  <h3>8.3. Advanced Options <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg></h3>
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

          <h3>8.4. Interpreting the Map</h3>
		  <p>
			When you click a point on the map an icon will appear showing the extraction location or region. 
			The icon will usually be a square with a point in the centre: the point shows where you  clicked and the 
			square shows the region in which data were extracted. The size of this square is controlled by the 
			Advanced Options 
			(<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84a.484.484 0 0 0-.48.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.488.488 0 0 0-.59.22L2.09 8.83a.488.488 0 0 0 .12.61l2.03 1.58c-.05.3-.07.63-.07.94s.02.64.07.94l-2.03 1.58a.488.488 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.27.41.48.41h3.84c.24 0 .44-.17.48-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.488.488 0 0 0-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg> ) 
			"Buffer" setting.
		  </p>
          <p>
            Use the layer controls in the top-left to toggle between <strong>Velocity</strong>, 
            <strong>Measurement Count</strong>, and <strong>Speed Trend</strong>. You can
			optionally overlay ice flow direction arrows and topography data.
		  </p>
		  <ul>
            <li><strong>Topography:</strong> A hillshaded digital elevation model of the area (Howat et al., 2015, 2022) (</li>
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
			</p>
			<p>
			Wallis, B.J., Hogg, A.E., Zhu, Y. and Hooper, A., 2024. Change in grounding line location on the Antarctic Peninsula measured using a tidal motion offset correlation method. The Cryosphere, 18(10), pp.4723-4742. https://doi.org/10.5194/tc-18-4723-2024.
			</p>
			<p>
				Howat, Ian, et al., 2022, “The Reference Elevation Model of Antarctica – Mosaics, Version 2”, https://doi.org/10.7910/DVN/EBW8UC, Harvard Dataverse, V1, [16/02/2026].
			</p>
			<p>
				Howat, I., Negrete, A. & Smith, B. (2015). MEaSUREs Greenland Ice Mapping Project (GIMP) Digital Elevation Model. (NSIDC-0645, Version 1). [Data Set]. Boulder, Colorado USA. NASA National Snow and Ice Data Center Distributed Active Archive Center. https://doi.org/10.5067/NV34YUIXLP9W. [describe subset used if applicable]. Date Accessed 02-16-2026.
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
		   
		  <h3>8.5. Interpreting the Chart</h3>
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
		  
		  <h3>8.6. Output</h3>
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

		<section id="how-to-use-datacube">
		  <h2>9. SHIVER Data Cube Extractor</h2>
		  <h3>9.1. Basic Usage</h3>
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
		  
          <h3>9.2. Uploading Files   
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
		  
          <h3>9.3. Interpreting the Map</h3>
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
		  
		  <h3>9.4. Output</h3>
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
			<em>If the data are exported any temporal resolution other than native, there could be these additional variables:</em>
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
		  
		</section>

        <section id="citation">
          <h2>10. Citation & License</h2>
          The recommended citation for this data is 
		  "Ice velocity generated using SHIFT (Davison et al., 2020; Tuckett et al., 2019) and provided by the FRAM/SHIVER project (Kingslake/Sole)."
		  <br>
		  <blockquote class="citation-block">
		  Davison, B.J., Sole, A.J., Cowton, T.R., Lea, J.M., Slater, D.A., Fahrner, D. and Nienow, P.W., 2020. Subglacial drainage evolution modulates seasonal ice flow variability of three tidewater glaciers in southwest Greenland. Journal of Geophysical Research: Earth Surface, 125(9), p.e2019JF005492. DOI: https://doi.org/10.1029/2019JF005492. 
		  </blockquote>
		  
		  <blockquote class="citation-block">
		  Tuckett, P.A., Ely, J.C., Sole, A.J., Livingstone, S.J., Davison, B.J., Melchior van Wessem, J. and Howard, J., 2019. Rapid accelerations of Antarctic Peninsula outlet glaciers driven by surface melt. Nature Communications 10, 4311. https://doi.org/10.1038/s41467-019-12039-2.
		  </blockquote>
		  
		  <blockquote class="citation-block">
		  Kingslake/Sole : Flow Response of Antarctic Ice to Meltwater/Sheffield Ice Velocity ExploreR
		  </blockquote>
		  <br>
		  FRAM, SHIFT and SHIVER were funded by NSFGEO-NERC grant #2053169.
        </section>

      </main>
    </div>

    <footer class="partners-footer">
      <div class="footer-content">
	  
        <div class="partner-group">
          <h4>Lead Institutions</h4>
		   <AppLink to="https://sheffield.ac.uk/" target="_blank" rel="noopener noreferrer">
			  <img :src="sheffieldLogo" alt="University of Sheffield" class="partner-logo" />
		   </AppLink>
		   <br>
		   <AppLink to="https://lamont.columbia.edu/" target="_blank" rel="noopener noreferrer">
			  <img :src="LDEOLogo" alt="LDEO" class="partner-logo" />
		   </AppLink>
        </div>
        
        <div class="partner-group">
          <h4>Funded By</h4>
		  <AppLink to="https://www.ukri.org/councils/nerc/" target="_blank" rel="noopener noreferrer">
			  <img :src="UKRILogo" alt="UKRI" class="partner-logo" />
		   </AppLink>
		  <br>
		  <AppLink to="https://www.nsf.gov/awardsearch/show-award/?AWD_ID=2053169" target="_blank" rel="noopener noreferrer">
			  <img :src="NSFLogo" alt="NSF" class="partner-logo" />
		   </AppLink>
		  <br>
		  The FRAM project is funded by NSFGEO-NERC <br>
		  Grant Number: #2053169, "Investigating the <br> 
		  Direct Influence of Meltwater on Antarctic Ice Sheet Dynamics"
        </div>
		
		<div class="partner-group">
          <h4>Powered by</h4>
		  <AppLink to="https://docs.hpc.shef.ac.uk/en/latest/stanage" target="_blank" rel="noopener noreferrer">
			  <img :src="StanageLogo" alt="Stanage" class="partner-logo" />
		   </AppLink>
		  <br>
		  SHIFT and SHIVER are powered by the University of Sheffield HPC Stanage <br>
        </div>
        
        <div class="partner-group">
          <h4>Contact</h4>
          <p>
		  SHIVER Project Team<br>
		  School of Geography and Planning, University of Sheffield, UK <br>
		  Email: shiver@sheffield.ac.uk
		  <br><br>
		  FRAM Project Team<br>
		  Lamont-Doherty Earth Observatory, Columbia University, USA
		  </p>
        </div>
		
      </div>
      <div class="copyright">
        &copy; {{ new Date().getFullYear() }} SHIVER Project. Licensed under GNU GPL-3.0.
      </div>
    </footer>

  </div>
</template>

<style scoped>
/* --- LAYOUT --- */
.doc-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fcfcfc;
}

.doc-container {
  display: flex;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 40px 20px;
  gap: 60px; /* Space between sidebar and text */
  flex: 1; /* Pushes footer down */
}

/* --- SIDEBAR --- */
.doc-sidebar {
  width: 250px;
  flex-shrink: 0;
  /* Sticky Magic: Keeps menu visible while scrolling */
  position: sticky;
  top: 40px; 
  height: fit-content;
  border-right: 2px solid #eee;
  padding-right: 20px;
}

.doc-sidebar h3 {
  margin-top: 0;
  color: #0b1e3b;
  text-transform: uppercase;
  font-size: 0.9rem;
  letter-spacing: 1px;
}

.doc-sidebar ul {
  list-style: none;
  padding: 0;
}

.doc-sidebar li {
  margin-bottom: 12px;
}

.doc-sidebar a {
  text-decoration: none;
  color: #555;
  font-weight: 500;
  transition: color 0.2s;
  display: block;
  padding: 5px 0;
}

.doc-sidebar a:hover {
  color: #0056b3;
  transform: translateX(5px); /* Slight slide effect */
}

/* --- MAIN CONTENT --- */
.doc-content {
  flex-grow: 1;
  max-width: 800px; /* Prevents lines from becoming too long to read */
}

section {
  margin-bottom: 60px;
  scroll-margin-top: 80px; /* Ensures header isn't hidden by navbar when jumping */
}

h1 {
  font-size: 2.5rem;
  color: #0b1e3b;
  margin-bottom: 20px;
}

h2 {
  font-size: 1.8rem;
  color: #0b1e3b;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
  margin-top: 0;
}

h3 {
  font-size: 1.3rem;
  color: #444;
  margin-top: 25px;
}

p, li {
  line-height: 1.7;
  color: #444;
  font-size: 1.05rem;
}

.intro-text {
  font-size: 1.2rem;
  color: #555;
  border-left: 4px solid #0056b3;
  padding-left: 20px;
}

.info-box {
  background: #eef7ff;
  padding: 20px;
  border-radius: 6px;
  border-left: 4px solid #5a9bd4;
  margin: 20px 0;
}

.citation-block {
  background: #f5f5f5;
  padding: 20px;
  font-family: 'Courier New', Courier, monospace;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.box-image {
  display: block;
  max-width: 100%;       /* Ensures image never exceeds box width */
  height: auto;          /* Maintains aspect ratio */
  margin: 15px 0;        /* Adds space above and below the image */
  border-radius: 4px;    /* Optional: slightly rounded corners */
  box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Optional: subtle shadow */
}

/* --- ICONS --- */
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

/* --- FOOTER STYLES (Copied from HomeView) --- */
.partners-footer {
  background-color: #0b1e3b;
  color: white;
  padding: 50px 20px 20px;
  margin-top: auto;
}

.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  gap: 40px;
  margin-bottom: 40px;
}

.partner-group {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.partner-group h4 {
  text-transform: uppercase;
  font-size: 0.9rem;
  color: #5a9bd4;
  margin-bottom: 15px;
  letter-spacing: 1px;
}

.partner-logo {
  height: 60px;
  width: auto;
  display: block;
  max-width: 100%;
  background-color: white;
  padding: 8px;
  border-radius: 6px;
  opacity: 0.9;
  margin-bottom: 10px;
}

.copyright {
  text-align: center;
  border-top: 1px solid rgba(255,255,255,0.1);
  padding-top: 20px;
  font-size: 0.8rem;
  color: #888;
}

/* --- RESPONSIVE --- */
@media (max-width: 768px) {
  .doc-container {
    flex-direction: column;
  }
  .doc-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 2px solid #eee;
    padding-bottom: 20px;
    margin-bottom: 20px;
    position: static; /* Disable sticky on mobile */
  }
}
</style>