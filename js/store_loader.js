/**
 * Módulo de Carregamento Assíncrono de Dados (Store Loader).
 * Carrega catálogos sob demanda particionados por loja via fetch, com cache em memória.
 */

const StoreLoader = {
  cache: {
    stores: {},
    analytics: null,
    moldes: null
  },

  async loadStore(storeKey) {
    if (this.cache.stores[storeKey]) {
      return this.cache.stores[storeKey];
    }

    try {
      const resp = await fetch(`./data/stores/${storeKey}.json`);
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status} ao carregar catálogo de ${storeKey}`);
      }
      const data = await resp.json();
      this.cache.stores[storeKey] = data;
      return data;
    } catch (err) {
      console.error(`Erro ao carregar loja ${storeKey}:`, err);
      // Fallback para quando MASTER_PAYLOAD foi pré-injetado ou carregamento offline
      if (window.MASTER_PAYLOAD && window.MASTER_PAYLOAD.stores && window.MASTER_PAYLOAD.stores[storeKey]) {
        return window.MASTER_PAYLOAD.stores[storeKey];
      }
      throw err;
    }
  },

  async loadAnalytics() {
    if (this.cache.analytics) return this.cache.analytics;
    try {
      const resp = await fetch('./data/stores/analytics.json');
      if (resp.ok) {
        this.cache.analytics = await resp.json();
        return this.cache.analytics;
      }
    } catch (e) {
      console.warn("Analytics json não carregado via fetch, verificando payload:", e);
    }
    if (window.MASTER_PAYLOAD && window.MASTER_PAYLOAD.analytics) {
      return window.MASTER_PAYLOAD.analytics;
    }
    return { history: [], available_csvs: [] };
  },

  async loadMoldes() {
    if (this.cache.moldes) return this.cache.moldes;
    try {
      const resp = await fetch('./data/stores/moldes.json');
      if (resp.ok) {
        this.cache.moldes = await resp.json();
        return this.cache.moldes;
      }
    } catch (e) {
      console.warn("Moldes json não carregado via fetch, verificando payload:", e);
    }
    if (window.MASTER_PAYLOAD && window.MASTER_PAYLOAD.moldes) {
      return window.MASTER_PAYLOAD.moldes;
    }
    return {};
  }
};
