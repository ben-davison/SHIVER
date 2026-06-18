import { driver } from "driver.js";
import "driver.js/dist/driver.css";

export function startGuestTour(onTourComplete, setStatusMessage) {
  let driverObj;
  let mapClickHandler = null;

  // 1. THE INTERCEPTOR: Stops Vue from seeing the click and shows a message
  const blockInteraction = (e) => {
    e.stopImmediatePropagation();
    e.stopPropagation();
    e.preventDefault();
    
    // Call the provided function instead of alert()
    if (setStatusMessage) {
      setStatusMessage("This feature is disabled during the tour.");
    }
  };

  driverObj = driver({
    showProgress: true,
    allowClose: true,
    
    // --- GLOBAL SETUP HOOK ---
    onHighlighted: (element, step, { driver }) => {
      // A. Final step completion
      if (driver.isLastStep()) {
        if (typeof onTourComplete === 'function') {
          onTourComplete();
        }
      }

      // B. Block clicks on specific buttons
      // If the highlighted element has an ID that includes 'btn', hijack its click
      if (element && element.id && element.id.includes('btn')) {
        // 'true' uses the Capture Phase, meaning this runs before anything else
        element.addEventListener('click', blockInteraction, true);
      }

      // C. Force Map Click on Step 4
      if (element && step.popover && step.popover.title === 'Extracting Data') {
        mapClickHandler = () => {
          driver.moveNext();
        };
        // Wait for the user to click the map, then auto-advance
        element.addEventListener('click', mapClickHandler, { once: true });
      }
    },

    // --- GLOBAL CLEANUP HOOK ---
    onDeselected: (element, step, { driver }) => {
      // A. Remove the button click block so it works normally after the tour
      if (element && element.id && element.id.includes('btn')) {
        element.removeEventListener('click', blockInteraction, true);
      }

      // B. Remove the map click listener (in case they clicked 'Previous' instead)
      if (element && step.popover && step.popover.title === 'Extracting Data') {
        if (mapClickHandler) {
          element.removeEventListener('click', mapClickHandler);
          mapClickHandler = null;
        }
      }
    },

    // Injects a custom "Skip Tour" text link on the left side of the footer
    onPopoverRender: (popover) => {
      if (document.getElementById("tour-skip-btn")) return;

      const skipBtn = document.createElement("button");
      skipBtn.id = "tour-skip-btn";
      skipBtn.innerText = "Skip Tour";
      
      skipBtn.className = "driver-popover-prev-btn"; 
      skipBtn.style.fontWeight = "normal";       
      skipBtn.style.fontSize = "13px";           
      skipBtn.style.letterSpacing = "-0.4px";    
      skipBtn.style.cursor = "pointer";          
      skipBtn.style.marginRight = "auto";        
      skipBtn.style.marginLeft = "20px";

      skipBtn.addEventListener("click", () => {
        driverObj.destroy(); 
      });

      if (popover.footerButtons) {
        popover.footerButtons.prepend(skipBtn);
      }
    },
    
    onDestroyed: () => {}, 

    steps: [
      {
        element: '.map-wrapper', 
        popover: {
          title: 'Welcome to the SHIVER Timeseries Explorer',
          description: "This quick tour will show you how to extract and visualize ice velocity data.",
          position: 'center'
        }
      },
      {
        element: '.map-wrapper', 
        popover: {
          title: 'Navigating the Map',
          description: "Use your mouse or trackpad to navigate the map to whichever glacier you're interested in. Click-and-drag to pan the map, and use your scroll wheel to zoom in and out. Why don't you try it now?",
        },
        onNextClick: (element, step, { driver }) => {
          driver.pause();
          setTimeout(() => driver.moveNext(), 1500);
        }
      },
      {
        element: '#btn-overlays', 
        popover: {
          title: 'Map overlays',
          description: 'Use the map overlays control panel to configure your map. This lets you explore maps of speed, speed trend, speed change and much more <strong>(account holders only)</strong>.',
        }
      },
      
      {
        element: '.map-wrapper',
        popover: {
          title: 'Extracting Data',
          description: "Click anywhere on the map to extract and plot a timeseries of ice velocity. You can plot up to ten timeseries at once.<br><strong>Click the map now to continue</strong>",
          showButtons: ['previous'] 
        }
      },
      {
        element: '#velocity-chart', 
        popover: { 
          title: 'Interactive Chart', 
          description: 'If you clicked the map, your timeseries will be plotted! On the chart, you can click-and-drag directly on the plot area to zoom in, click the paint palette icon to reveal the data sources, and much more!' 
        }
      },
      {
        element: '#chart-axis-controls', 
        popover: { 
          title: 'Fine-tune the View', 
          description: 'These buttons let you manually adjust and fine-tune the axes limits to view a specific date range or speed range.' 
        }
      },
      {
        element: '#btn-toggle-trends', 
        popover: { 
          title: 'Trend Lines', 
          description: 'This button lets you calculate and overlay linear trends on your data.' 
        }
      },
      {
        element: '#btn-advanced', 
        popover: {
          title: 'Advanced timeseries options',
          description: 'With the advanced options, you can filter for particular data sources, fill gaps in your data and smooth your timeseries <strong>(account holders only)</strong>.',
        }
      },
      {
        element: '#btn-download-data', 
        popover: {
          title: 'Download your data',
          description: 'You can download all of the data shown in the chart to an excel document by clicking this button.',
        }
      },
      {
        element: '#btn-download-chart', 
        popover: {
          title: 'Download your chart',
          description: 'You can download your chart to a .png file by clicking this button',
        }
      },
      {
        element: '#btn-upload-file', 
        popover: {
          title: 'Upload a file',
          description: 'Clicking here allows you to upload a shapefile, KML, KMZ or GeoJSON to extract timeseries much more precisely and repeatably.',
        }
      },
      {
        element: '#btn-switch-antarctica', 
        popover: {
          title: 'Explore Antarctica',
          description: 'Clicking here changes the map so that you can view and explore Antarctica.',
        }
      },
      {
        element: '#btn-login', 
        popover: {
          title: 'Create an account or log in',
          description: 'You can access more data and many more functions by creating an account and logging in.',
        }
      },
      {
        element: '#btn-help-trigger',
        popover: {
          title: 'Need Help?',
          description: 'You can find much more detailed instructions and guidance in the SHIVER help menu.',
        },
      }
    ]
  });

  driverObj.drive();
}