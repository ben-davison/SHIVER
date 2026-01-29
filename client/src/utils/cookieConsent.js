import * as CookieConsent from "vanilla-cookieconsent";
import "vanilla-cookieconsent/dist/cookieconsent.css";

// --- Safely import bootstrap ---
// We import the whole module and try both locations to handle the build error
import * as VueGtagModule from "vue-gtag";
const bootstrap = VueGtagModule.bootstrap || VueGtagModule.default?.bootstrap;

export const initCookieConsent = () => {
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

    // --- ON CONSENT ---
    onConsent: ({ categories }) => {
      if (categories.includes("analytics")) {
        console.log("? Consent granted. Bootstrapping GA4...");
        // valid 'bootstrap' call (requires plugin to be installed in main.js)
        if (bootstrap) bootstrap(); 
      }
    },
    
    // --- ON CHANGE ---
    onChange: ({ changed_categories, categories }) => {
      if (changed_categories.includes("analytics")) {
        if (categories.includes("analytics")) {
           if (bootstrap) bootstrap(); 
        } else {
           location.reload(); 
        }
      }
    }
  });
};