/**
 * y12.ai RMM - Frontend Configuration
 * This file is served statically and provides branding and authentication configuration
 */

window.Y12_CONFIG = {
  // Branding
  productName: 'y12.ai RMM',
  companyName: 'y12.ai',
  domain: 'rmm.y12.ai',

  // Theme
  theme: {
    primaryColor: '#2563eb',
    secondaryColor: '#10b981',
    darkMode: true,
  },

  // Authentication
  auth: {
    // Google OAuth is the primary authentication method
    googleAuthEnabled: true,
    localAuthEnabled: false,  // Disabled when Google auth only

    // OAuth endpoints
    endpoints: {
      authConfig: '/accounts/auth/config/',
      googleCallback: '/accounts/google/login/callback/',
      ssoToken: '/accounts/ssoproviders/token/',
    }
  },

  // API Configuration
  api: {
    version: 'v2',
    timeout: 30000,
  },

  // Feature Flags
  features: {
    webTerminal: false,  // Disabled for security in cloud deployment
    serverScripts: true,
    reporting: true,
  }
};

// Freeze configuration to prevent modification
Object.freeze(window.Y12_CONFIG);
Object.freeze(window.Y12_CONFIG.theme);
Object.freeze(window.Y12_CONFIG.auth);
Object.freeze(window.Y12_CONFIG.auth.endpoints);
Object.freeze(window.Y12_CONFIG.api);
Object.freeze(window.Y12_CONFIG.features);
