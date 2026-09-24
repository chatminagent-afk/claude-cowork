'use strict';

const N8N_GET_URL = 'https://DOMAIN-N8N-ANDA/webhook/tracking-get';
const N8N_UPDATE_URL = 'https://DOMAIN-N8N-ANDA/webhook/tracking-update';

const CONFIG = {
  N8N_GET_URL: N8N_GET_URL,
  N8N_UPDATE_URL: N8N_UPDATE_URL,
  API_GET_URL: N8N_GET_URL,
  API_UPDATE_URL: N8N_UPDATE_URL,
  FETCH_TIMEOUT_MS: 8000,
  MAX_RETRY: 2,
  RETRY_BACKOFF_MS: 1500,
  CACHE_KEY_PREFIX: 'metro_track_',
  OFFLINE_QUEUE_KEY: 'metro_admin_queue',
  ADMIN_NAME_KEY: 'metro_admin_name',
  APP_NAME: 'Metro Logistik Indonesia',
  ENUM_STATUS: [
    'Manifest',
    'On Process',
    'Transit',
    'Out for Delivery',
    'Delivered',
    'Failed/Return'
  ]
};

if (typeof window !== 'undefined') {
  window.CONFIG = CONFIG;
}
