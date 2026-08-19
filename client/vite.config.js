import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Sitemap from 'vite-plugin-sitemap'

const shiverRoutes = [
  '/SHIVER/',
  '/SHIVER/map',
  '/SHIVER/cube',
  '/SHIVER/documentation/overview',
  '/SHIVER/documentation/greenland',
  '/SHIVER/documentation/antarctic',
  '/SHIVER/documentation/shift',
  '/SHIVER/documentation/datacubegen',
  '/SHIVER/documentation/timeseriesexplore',
  '/SHIVER/documentation/cubeextract',
  '/SHIVER/documentation/cloud',
  '/SHIVER/documentation/citation',
  '/SHIVER/documentation/projects/overview',
  '/SHIVER/documentation/projects/people'
]

export default defineConfig({
  base: '/SHIVER/', 
  plugins: [
    vue(),
    Sitemap({
      // 2. Use the bare domain (the subfolder is handled by your routes array)
      hostname: 'https://shiver-ice-velocity.github.io', 
      
      // 3. Tell the plugin to ignore its incomplete auto-scan root
      exclude: ['/'],
      
      // 4. Force feed the explicit routes so timing issues don't matter
      dynamicRoutes: shiverRoutes
    })
  ],
  ssr: {
    noExternal: ['file-saver']
  }
})