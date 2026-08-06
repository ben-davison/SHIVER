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
      <h1>Ice Velocity Data Cubes</h1>
      <p class="intro-text">
        This page describes our ice velocity data cubes - what they are and how we create them.
      </p>
    </section>

    <section id="what_zarr">
      <h2>5.1. What is Zarr</h2>
	  <ZoomableFigure caption="Credit: https://www.earthmover.io/blog/what-is-zarr">
			<img src="../../assets/documentation/zarr/what-is-zarr.gif" alt="Zarr gif">
      </ZoomableFigure>
      <p>
	  Much of the following text is based on more comprehensive descriptions of Zarr in
	  <AppLink to="https://zarr.dev/" target="_blank" rel="noopener" class="text-link">zarr.dev</AppLink> and 
	  <AppLink to="https://www.earthmover.io/blog/what-is-zarr" target="_blank" rel="noopener" class="text-link">earthmover.io</AppLink>.
	  </p>
	  <p>
	  Zarr is a powerful open-source, cloud-native protocol for storing chunked, compressed N-dimensional arrays. It is designed for performance, 
	  interoperability and cloud computing or other parallel computing application. It enables high-throughput distributed I/O, allows concurrent read/write
	  from multiple threads or processes. In a world where data is abundant, traditional data formats can become a bottleneck in a workflow - zarr removes that bottleneck.
	  </p>
	  <ZoomableFigure caption="Fig 5.1: Zarr logo">
			<img src="../../assets/documentation/zarr/zarr.png" alt="Zarr logo">
      </ZoomableFigure>
	  <p>
	  Zarr is specifically designed for tensor data (a.k.a multi-dimensional arrays) rather than tabular data. In a Zarr, structured data are stored in a compact
	  binary columnar (or chunked) layout, with encoding and compression appled to each chunk separately. In this way, it eliminates all possible redundant 
      information and is an 'array-native' data system. These chunks are small, manageable pieces of a large array or arrays that can be read and written independently.
      Crucially, Zarr chunks must be uniform, fixed-size blocks and the user must choose how large chunks should be in each dimension. The chunk size definition 
      strongly influences the performance of the Zarr for certain tasks - for time-series extraction, one would choose chunks that resemble towers (i.e. spanning many
	  elements in the time-dimension but few in the horizontal dimensions), whereas if the aim is to optimise spatial operations, flatter chunks would be more performant. 
	  Each chunk is saved as a separate binary file and is organized using a nested directory structure depending on the chunk position. Zarr also uses structured
	  metadata that enabled rapid identification of the required chunk(s) and lazy loading of datasets. 
	  </p>
	  <ZoomableFigure caption="Fig 5.2: Zarr chunk cartoon.">
			<img src="../../assets/documentation/zarr/zarr_chunk.png" alt="Zarr chunks">
      </ZoomableFigure>
	  <br>
    </section>
	
	
	<section id="working_zarr">
      <h2>5.2. Working with Zarr</h2>
	  <p>A growing ecosystem of tools is developing alongside Zarr that make it easier to work with large datasets. </p>
	  <p>
	  Xarray provides a high-level, labelled array interface that works seamlessly with Zarr. Where Zarr focuses on how data are stored, Xarray focuses on 
      how it is accessed. It enhances raw Zarr arrays by adding coordinate labels, metadata and powerful slicing capabilities, which together make it ideal for 
	  many scientific datasets. Xarray also enables lazy loading of Zarr data, where only the metadata is read into memory along with small portions of the 
	  actual data as needed. This makes it ideal for working with arrays that would be too large to load into memory. 
	  </p>
	  <p>
	  Dask brings parallelism and scalability to Zarr. Dask is a parallel and distributed computing library. In cloud computing or HPC
	  environments, it allows maximization of computing resources to work on many Zarr chunks in parallel because it manages how
	  chunks are distributed between workers.
	  </p>
	  <br>
	</section>
	
	
	<section id="building_zarr">
      <h2>5.3. Ice Sheet Zarr Stores</h2>
	  <p> 
	  Our ice sheet velocity Zarr stores contain ice velocity estimates that have been generated over years of effort by many research groups. 
	  These datasets are described in our 
	  <AppLink to="/documentation/greenland" class="text-link">Greenland Data Sources</AppLink> and 
	  <AppLink to="/documentation/antarctic" class="text-link">Antarctic Data Sources</AppLink> documentation pages. 
	  The ingested datasets have been released at a range of spatial resolutions and spatial extents, as appropriate to the underlying image resolution
	  and processing choices. Since Zarr stores are inherently structured, we had to interpolate every dataset to a common grid - these grids 
	  span the entirety of Greenland and Antarctica at 200 x 200 m resolution. For all datasets, the interpolation method was nearest neighbour. 
	  We also included error estimates in our Zarr, either using those provided with the original datasets or by assuming that the error is 5% of the
	  speed. 
	  </p>
	  <p>
	  For each ice sheet, we have three zarr stores. One has a chunk definition optimised for spatial analysis, another is optimised for 
	  timeseries analysis and another is balanced between the two.
	  </p>
	  <p>
	  Updates to the Greenland Zarr store are automated, though currently only one of the Contributing Datasets (PROMICE) is routinely updated. 
	  </p>
	  
	  <br>
	</section>
	
	
	
	

  </div>
</template>