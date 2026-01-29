import * as CookieConsent from "vanilla-cookieconsent";
import VueGtag from "vue-gtag"; // Import the default package (Works better with Vite)

// We now accept 'app' and 'router' as arguments
export const initCookieConsent = (app, router) => {
  CookieConsent.run({
    gui_options: {
      consent_modal: {
        layout: "box",
        position: "bottom left",
        equal_weight_buttons: true,
        flip_buttons: false,
      },
      preferences_modal: {
        layout: "box",
        position: "right",
        equal_weight_buttons: true,
        flip_buttons: false,
      },
    },
    categories: {
      necessary: { readOnly: true },
      analytics: { enabled: false }
    },
    language: {
      default: "en",
      translations: {
        en: {
          consent_modal: {
            title: "We use cookies",
            description: "We use cookies to analyze traffic. You can choose to accept analytics or browse without them.",
            primary_btn: { text: "Accept All", role: "accept_all" },
            secondary_btn: { text: "Reject All", role: "accept_necessary" },
          },
          preferences_modal: {
            title: "Cookie Preferences",
            accept_all_btn: "Accept All",
            reject_all_btn: "Reject All",
            save_btn: "Save Preferences",
            close_btn_label: "Close",
            sections: [
              { title: "Strictly Necessary", description: "Essential for the website to function.", linked_category: "necessary" },
              { title: "Analytics", description: "Tracks anonymous usage data.", linked_category: "analytics" }
            ],
          },
        },
      },
    },

    // Load analytics tool if cookies accepted
    onConsent: ({ categories }) => {
      if (categories.includes("analytics")) {
        console.log("? Consent granted. Installing Google Analytics...");
        
        // We manually install the plugin NOW. 
        // This injects the script tag and starts processing events.
        app.use(VueGtag, {
          config: { id: "G-4YGWRB6RCZ" } // Your real ID
        }, router);
      }
    },
    
    onChange: ({ changed_categories, categories }) => {
      if (changed_categories.includes("analytics")) {
        if (categories.includes("analytics")) {
           // Enable if switched ON
           app.use(VueGtag, {
              config: { id: "G-4YGWRB6RCZ" }
           }, router);
        } else {
           // Reload to clear cookies if switched OFF
           location.reload(); 
        }
      }
    }
  });
};