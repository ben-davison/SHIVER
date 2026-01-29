import * as CookieConsent from "vanilla-cookieconsent";
import { bootstrap } from "vue-gtag"; // Import the helper to manually start GA

export const initCookieConsent = () => {
  CookieConsent.run({
    // 1. UI Configuration
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

    // 2. Categories (Necessary is read-only, Analytics is toggleable)
    categories: {
      necessary: {
        readOnly: true,
      },
      analytics: {
        enabled: false // Default to disabled (GDPR requirement)
      }
    },

    // 3. Language & Text
    language: {
      default: "en",
      translations: {
        en: {
          consent_modal: {
            title: "We use cookies",
            description: "We use cookies to analyze website traffic and improve your experience. <br> You can choose to accept only necessary cookies or allow analytics.",
            primary_btn: {
              text: "Accept All",
              role: "accept_all", // 'accept_selected' or 'accept_all'
            },
            secondary_btn: {
              text: "Reject All",
              role: "accept_necessary",
            },
            footer: '<a href="#privacy">Privacy Policy</a>'
          },
          preferences_modal: {
            title: "Cookie Preferences",
            accept_all_btn: "Accept All",
            reject_all_btn: "Reject All",
            save_btn: "Save Preferences",
            close_btn_label: "Close",
            sections: [
              {
                title: "Strictly Necessary",
                description: "These cookies are essential for the proper functioning of the website.",
                linked_category: "necessary",
              },
              {
                title: "Performance & Analytics",
                description: "These cookies allow us to measure visits and traffic sources so we can improve the performance of our site.",
                linked_category: "analytics",
              },
            ],
          },
        },
      },
    },

    // 4. THE IMPORTANT PART: Triggers when user accepts
    onConsent: ({ categories }) => {
      if (categories.includes("analytics")) {
        console.log("? Analytics consent granted. Starting GA4...");
        bootstrap().then((gtag) => {
          // Optional: You can explicitly set consent mode here if needed
          // gtag('consent', 'update', { 'analytics_storage': 'granted' });
        });
      }
    },
    
    // 5. Triggers if user changes their mind later
    onChange: ({ changed_categories, categories }) => {
      if (changed_categories.includes("analytics")) {
        if (categories.includes("analytics")) {
          bootstrap(); // Enable if switched ON
        } else {
          location.reload(); // Force reload to clear cookies if switched OFF (Safest method)
        }
      }
    }
  });
};
