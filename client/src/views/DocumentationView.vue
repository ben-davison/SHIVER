<script setup>
/**
 * DOCUMENTATION VIEW
 * A text-heavy page with a sticky sidebar for easy navigation.
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

const publicPath = import.meta.env.BASE_URL;


</script>

<template>
  <div class="doc-page">
    
    <div class="doc-container">
      
      <aside class="doc-sidebar">
        <nav>
          <h3>Contents</h3>
          <ul>
            <li><a href="#introduction">Introduction</a></li>
            <li><a href="#overview">1. Overview</a></li>
            <li><a href="#data-sources">2. Data Sources</a></li>
			<li><a href="#pre-processing">3. Pre-processing</a></li>
			<li><a href="#algorithms">4. Measurement Algorithms</a></li>
			<li><a href="#post-processing">5. Post-processing</a></li>
			<li><a href="#mosaics">6. Mosaics</a></li>
			<li><a href="#automation">7. Automation</a></li>
            <li><a href="#how-to-use">8. SHIVER User Guide</a></li>
            <li><a href="#citation">9. Citation & License</a></li>
          </ul>
        </nav>
      </aside>

      <main class="doc-content">
        
        <section id="introduction">
          <h1>Introduction</h1>
          <p class="intro-text">
            Welcome to the technical documentation for <strong>SCADI</strong> (Sentinel-1 Cross-correlation for Accurate Determination of Ice velocity)
            and <strong>SHIVER</strong> (SHeffield Ice Velocity ExploreR). This platform provides access to high-resolution ice velocity time-series data 
			derived from Sentinel-1 Synthetic Aperture Radar (SAR) imagery.
          </p>
        </section>


        <section id="overview">
          <h2>1. Overview of approach</h2>
          <p>
            The velocity fields are derived using intensity tracking algorithms applied to consecutive Sentinel-1 image pairs. 
            Our processing pipeline is fully automated and involves:
          </p>
          <ul>
            <li><strong>Metadata curation and data download:</strong> At least daily, our system collates information about all Sentinel-1 images that have 
			been acquired over Greenland and Antarctica and identifies all potential image pairs. For each available image pair that hasn't yet been processed,
			it downloads the images, orbital positioning information and digitial elevation models required to complete the processing. All data download and curation 
			is completed 'on-the-fly' to minimise storage requirements.</li>
            <li><strong>Pre-processing:</strong>We use the open-source software GMTSAR to prepare the raw radar images for feature tracking and generate the
			information required to convert the images from radar to map coordinates. This process ingests the raw radar images, orbital data and elevation data.</li>
            <li><strong>Feature/intensity/speckle tracking:</strong> 2D fields of ice velocity are estimated and posted at 150x150 m resolution using standard methods.</li>
			<li><strong>Post-processing:</strong> Individual velocity fields are filtered to remove outliers, which are defined using cross-correlation quality metrics and 
			based on the characteristics of the retrieved flow field.</li>
			<li><strong>Mosaic creation:</strong> The 'raw' velocity fields derived from Sentinel-1 swaths are warped to a common grid and further corrections 
			and outlier removal routines are applied.</li>
          </ul>
        </section>


        <section id="data-sources">
          <h2>2. Data Sources</h2>
          <p>
            <strong>Sentinel-1:</strong> The European Space Agency (ESA) Sentinel-1 missions comprises a constellation of two sun-synchronous polar-orbiting satellites,
			which operate  in the same orbital plane with 180 degree phasing difference. It performs C-band Synthetic Aperture Radar (SAR) imaging, enabling day and night 
			acquisitions regardless of weather. 
		   </p>
			
			<figure style="text-align: center; margin: 20px 0;">
			 <img src="../assets/documentation/S1cartoon.jpg" alt="Sentinel-1 radar vision" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
			 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
			   Fig. 2.1: Artistic impression of Sentinel-1 image acquisition.
			 </figcaption>
		  </figure>
		  			
			<div class="info-box">
			  <p>
				<strong>What is a radar image?</strong> 
				Radar imaging is an "active" data collection technique where the satellite radar transmits its own pulses of energy and records the amount reflected back 
				from the Earth's surface - surfaces that reflect more energy back appear brighter. Typically, rougher surfaces and surfaces oriented towards the incoming radar waves 
				appear brighter than smooth surfaces or those that are in the 'radar shadow'. Surface properties also affect how much of the incoming radar signal is returned to the
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
				  Fig. 2.2: A Sentinel-1 radar image animation, showing the retreat of Wilkinson Murphy Glacier, Antarctica.
				</figcaption>
			  </figure>
			  <p>
				For our processing in SCADI, we use Sentinel-1 Level-1 Single Look Complex (SLC) images. SLC images represent the 'raw' radar returns from the ground surface,
				processed into a 2D image, but before those radar returns have been projected onto the ground surface. Since it has not been projected, the raw SLC image is in 
				'slant range' or 'line-of-sight' geometry, as if you are viewing the surface from the perspective of the satellite antenna without knowing anything about the 
				ground topography.
			  </p>
			</div>
			
			
		 <p>
			Sentinel-1A was launched on 3 April 2014, Sentinel-1B was launched on 25 April 2016, Sentinel-1C was launched on 5 December 2024 and Sentinel-1D was 
			launched on 4 November 2025. Sentinel-1B experienced a 
			<a href="https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Mission_ends_for_Copernicus_Sentinel-1B_satellite" target="_blank" rel="noopener" class="text-link">failure of the power supply</a>.
			on 23 December 2021, leaving it unable to deliver images.
			<br><br>
			Each of these individual satellites orbits the Earth in a consistent pattern. This allows them to image the same location on the ground every 12-days (so-called 'repeat' imagery). 
			Since each pair of satellites orbit the Earth 180 degrees apart but in the same orbital plane, we can combine the images from pairs of Sentinel-1 satellites to acquire repeat
			images every six days. Since our ice velocity measurements require us to measure the movement of surface features over some time period, this repeat image acquisition time
			period means that our velocity measurements represent the average ice speed during the time period between image acquisitions (which must be a multiple of six days).
					
			The Sentinel-1 SAR instrument can acquire images in 
		    <a href="https://sentiwiki.copernicus.eu/web/s1-products" target="_blank" rel="noopener" class="text-link">four exclusive modes</a>:
		</p>
		   <ul>
              <li><strong>Stripmap:</strong> the standard mode.</li>
              <li><strong>Interferometric Wide swath:</strong> where three 'swaths' of data are acquired using the <a href="https://ieeexplore.ieee.org/document/1677745" target="_blank" rel="noopener" class="text-link">TOPSAR</a> technique.</li>
              <li><strong>Extra Wide swath:</strong> where five 'swaths' of data are acquired using the TOPSAR technique, but at lower resolution to the IW mode.</li>
			  <li><strong>Wave:</strong> where small 'vignettes' of data are acquired at 100 km along-track intervals, alternating between near- and far-range incidence angles.</li>
          </ul>
		  
		  <p>
			For our processing in SCADI, we use images acquired in Interferometric Wide swath mode.
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
			   You can read more about SAR <a href="https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar" target="_blank" rel="noopener" class="text-link">here</a>.
             </p>
			</div>
			
			<p>
				Sentinel-1 Single Look Complex (SLC) data are provided in various polarisation, but HH (horizontal emit and horizontal receive) is best for ice velocity estimation. 
			</p>
		
          
        </section>
		
		
		<section id="pre-processing">
          <h2>3. Pre-processing</h2>
          <p>
            We use <a href="https://topex.ucsd.edu/gmtsar/" target="_blank" rel="noopener" class="text-link">GMTSAR</a> to convert Sentinel-1 SLC IW 
			image pairs to co-registered, geocoded amplitude images suitable for feature tracking. In the following, the first and second image in the image pair is referred to as image1
			and image2, respectively.
		  </p>
			<ul>
              <li><strong>Geometric alignment, deramping and burst stitching:</strong> We use information about the satellite position and the ground surface to align image2
					  with image 1. Deramping removes the phase ramp inherent in TOPS (Terrain Observation with Progressive Scans) data, resulting from the steering of the antenna
					  beam during acquisition, to ensure phase continuity. Two levels of 
					  <a href="https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html" target="_blank" rel="noopener" class="text-link">orbital information</a> 
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
			Our core processing pipeline is adapted from <strong>PIVSuite</strong> 
			(<a href="https://openresearchsoftware.metajnl.com/articles/10.5334/jors.334" target="_blank">Thielicke and Stamhuis, 2014</a>). 
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
			  resolutions in the range and azimuth directions (nominally 2.3 x 14.1 m), we use different IA lengths in each direction. 
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
			<a href="https://opg.optica.org/ol/fulltext.cfm?uri=ol-33-2-156" target="_blank">Guizar-Sicairos et al. (2008)</a>.
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
				<a href="https://www.mdpi.com/2072-4292/9/10/1062" target="_blank">Luttig et al. (2017)</a>.
			   </p>
				
				<figure style="text-align: center; margin: 20px 0;">
					 <img src="../assets/documentation/segfilt_crop.png" alt="Adapted version of Figure 5 from Luttig et al. 2017" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
					 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
					   Fig. 5.1: An illustration of the segmentation filter removing groups of outliers from the left image to produce the righthand image. Adapted from Luttig et al. (2017) Figure 5.
					 </figcaption>
				</figure>
			  

			  <h3>5.2. Stage 2: Ionospheric Destriping</h3>
			  <p>
				Velocity fields derived from Synthetic Aperture Radar data often suffers from 'striping' artifacts caused by ionospheric irregularities interfering with the radar signal. 
			  </p>
			  
			  <p>
				We conditonally apply a general destriping algorithm described by 
				<a href="https://opg.optica.org/oe/fulltext.cfm?uri=oe-33-3-5800" target="_blank">Rottmayer et al. (2025)</a>. 
			  </p>
			  <div class="info-box">
				<strong>Conditional Application:</strong> 
				Blindly filtering data can degrade valid high-resolution features. Therefore, our pipeline calculates noise metrics 
				(using BRISQUE and other noise estimation functions) <em>before</em> and <em>after</em> the filter runs. 
				The destriped result is only accepted if the algorithm detects a quantifiable reduction in noise levels. This is necessary
				in part because stripes can only be clearly detected (and removed) if the velocity field is relatively complete - large gaps
				or significant noise from other sources can hinder stripe detection.
			  </div>
			  
			  <figure style="text-align: center; margin: 20px 0;">
					 <img src="../assets/documentation/destripe.png" alt="Example destriping" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
					 <figcaption style="font-size: 0.9rem; color: #666; margin-top: 5px;">
					   Fig. 5.2: An illustration of striping in a velocity field and the effect of stripe removal.
					 </figcaption>
			  </figure>

			  <h3>5.3. Stage 3: Map Projection & Outlier Removal</h3>
			  <p>
				Once the data is cleaned in radar coordinates, it is projected onto the ground surface map geometry. This converts displacements from "pixels" into "meters" and corrects for topographic distortion.
			  </p>
			  <p>
				We then run a final suite of physical and statistical filters, always attempting to remove outliers whilst minimising loss of 'good' data:
			  </p>

			  <ul>
				<li>
				  <strong>Signal-to-Noise Ratio (SNR):</strong> 
				  We reject any vectors where the cross-correlation peak strength is low relative to the noise floor. We utilize a threshold of <strong>SNR > 5.8</strong>, 
				  (i.e. velocity estimates with an SNR of less than 5.8 are removed). This threshold was established as a robust cutoff for feature tracking by 
				  <a href="https://ieeexplore.ieee.org/document/4261046" target="_blank">de Lange et al. (2007)</a>.
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
				To create an analysis-ready product, we must standardize these all swath-based velocity fields onto a common grid. 
				We achieve this by generating <strong>date-pair Mosaics</strong>.
			  </p>

			  <h3>6.1. "Raw" Mosaics</h3>
			  <p>
				The "Raw" mosaic process aggregates all velocity data derived from any Sentinel-1 pair covering the same time window 
				(e.g., all data measuring displacement between Date A and Date B). It also removed offsets in velocity estimates between
				overlapping swaths and removed biases detected in bedrock areas (where zero motion is expected, but not always measured).
			  </p>
			  
			  <h4>Step 1: Common Grid Projection</h4>
			  <p>
				We define a master 'Common Grid' that covers the entire study area (e.g., the full Antarctic Peninsula or West Greenland). 
				Using <strong>GDAL</strong> (Geospatial Data Abstraction Library) tools, every individual swath is warped and interpolated 
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

			  <h4>Step 3: Error and bias correction</h4>
			  <p>
				Errors in the resulting velocity fields may step from errors in the calculated satellite position, errors caused by ionospheric interference with the 
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

			  <h4>Step 4: Spatial Filtering</h4>
			  <p>
				Once merged and bias-corrected, we apply a <strong>Hybrid Median Filter</strong> to the mosaic. This filter is specifically chosen because it effectively 
				removes "salt-and-pepper" noise (random, high-frequency outliers) in the data, while preserving sharp edges—crucial for maintaining the distinct 
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
			Our complete automation workflow is available in the document below. We use a SpatioTemporal Asset Catalog (STAC)-like architecture
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
			  data="/pdfs/SCADI_UserGuide.pdf" 
			  type="application/pdf" 
			  width="100%" 
			  height="800px"
			>
			  <div style="padding: 20px; text-align: center;">
				<p>It appears you don't have a PDF plugin for this browser.</p>
				<a href="/pdfs/SCADI_UserGuide.pdf" class="btn-download">
				  Click here to download the User Guide
				</a>
			  </div>
			</object>
		  </div>
        </section>
		
		
        <section id="how-to-use">
		  <h2>8. SHIVER User Guide</h2>
		  <h3>8.1. Selecting Data</h3>
          <p>
            Click anywhere on the map to view a time-series of ice velocity at that point. 
            You can select up to ten points to compare different locations.
          </p>

          <h3>8.2 Uploading Shapefiles</h3>
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

          <h3>8.3 Interpreting the Map</h3>
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
		  
		  <h3>8.4 Output</h3>
          <p>
            Download your timeseries as <strong>.csv</strong> files and/or the graph as a , 
            <strong>.png</strong> file. If multiple points are selected, the extracted timeseries will be 
			downloaded as a <strong>.zip</strong> file containing multiple .csv files. Downloads will
			also include a geojson of your point locations.
		  </p>
		  <p>
            <strong>CSV output variables:</strong>
		  </p>
          <ul>
            <li><strong>Date:</strong> The central date of the two images used to estimate ice speed</li>
            <li><strong>Speed_m_yr:</strong> Horizontal surface ice speed in metres per year. If a buffer is used, the median speed within the resulted area is used.</li>
            <li><strong>Error_m_yr:</strong> An estimate of the global uncertainty in ice speed at this time period. Defined as the median speed over bedrock regions at that time.</li>
			<li><strong>Time_separation_days:</strong> The number of days between the two images used to estimate ice speed. So the first image was acquired on Date-Time_separation_days/2, and the second image on Date+Time_separation_days/2.</li>
			<li><strong>Pixel_Count:</strong> The number of valid speed estimates in the extraction location. This will be 1 if buffer=0. Pixel resolution is 200 metres, so the maximum value for e.g. a 500 m buffer is 25 (1000 x 1000 metre region = 5 x 5 pixel region).</li>
		  </ul>
		
        </section>


        <section id="citation">
          <h2>9. Citation & License</h2>
          The recommended citation for this data is 
		  "Ice velocity generated using SCADI (Davison et al., 2020; Tuckett et al., 2019) and provided by the FRAM/SHIVER project (Kingslake/Sole)."
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
        </section>

      </main>
    </div>

    <footer class="partners-footer">
      <div class="footer-content">
	  
        <div class="partner-group">
          <h4>Lead Institutions</h4>
		   <a href="https://sheffield.ac.uk/" target="_blank" rel="noopener noreferrer">
			  <img :src="sheffieldLogo" alt="University of Sheffield" class="partner-logo" />
		   </a>
		   <br>
		   <a href="https://lamont.columbia.edu/" target="_blank" rel="noopener noreferrer">
			  <img :src="LDEOLogo" alt="LDEO" class="partner-logo" />
		   </a>
        </div>
        
        <div class="partner-group">
          <h4>Funded By</h4>
		  <a href="https://www.ukri.org/councils/nerc/" target="_blank" rel="noopener noreferrer">
			  <img :src="UKRILogo" alt="UKRI" class="partner-logo" />
		   </a>
		  <br>
		  <a href="https://www.nsf.gov/awardsearch/show-award/?AWD_ID=2053169" target="_blank" rel="noopener noreferrer">
			  <img :src="NSFLogo" alt="NSF" class="partner-logo" />
		   </a>
		  <br>
		  The FRAM project is funded by NSFGEO-NERC <br>
		  Grant Number: # 2053169, "Investigating the <br> 
		  Direct Influence of Meltwater on Antarctic Ice Sheet Dynamics
        </div>
		
		<div class="partner-group">
          <h4>Powered by</h4>
		  <a href="https://docs.hpc.shef.ac.uk/en/latest/stanage" target="_blank" rel="noopener noreferrer">
			  <img :src="StanageLogo" alt="Stanage" class="partner-logo" />
		   </a>
		  <br>
		  SCADI and SHIVER are powered by the University of Sheffield HPC Stanage <br>
        </div>
        
        <div class="partner-group">
          <h4>Contact</h4>
          <p>
		  SHIVER Project Team<br>
		  School of Geography and Planning, University of Sheffield, UK
		  <br><br>
		  FRAM Project Team<br>
		  Lamont-Doherty Earth Observatory, Columbia University, USA
		  </p>
        </div>
		
      </div>
      <div class="copyright">
        &copy; {{ new Date().getFullYear() }} SHIVER Project. All rights reserved.
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