/**
 * Módulo de Carregamento Assíncrono Universal (Store Loader).
 * Suporta 100% tanto abertura local por duplo clique (protocolo file:// sem erro de CORS)
 * quanto execução em servidores HTTP/HTTPS (Vercel) com cache inteligente em memória.
 */

const StoreLoader = {
  cache: {
    stores: {},
    analytics: null,
    moldes: null
  },

  /**
   * Injeta um script dinamicamente no documento para contornar qualquer restrição de CORS no file://
   */
  loadScript(src) {
    return new Promise((resolve, reject) => {
      // Se o script já foi adicionado
      const existingScript = document.querySelector(`script[src="${src}"]`);
      if (existingScript) {
        return resolve();
      }

      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.onload = () => resolve();
      script.onerror = (err) => reject(new Error(`Falha ao carregar script ${src}`));
      document.head.appendChild(script);
    });
  },

  async loadStore(storeKey) {
    // 1. Verificar cache em memória
    if (this.cache.stores[storeKey]) {
      return this.cache.stores[storeKey];
    }

    const varName = `__STORE_${storeKey.toUpperCase()}`;

    // 2. Verificar se a variável global já foi pré-carregada
    if (window[varName]) {
      this.cache.stores[storeKey] = window[varName];
      return window[varName];
    }

    // 3. Tentar carregar via injeção dinâmica de script (.js) - Funciona 100% no file:// e em http://
    try {
      await this.loadScript(`data/stores/${storeKey}.js`);
      if (window[varName]) {
        this.cache.stores[storeKey] = window[varName];
        return window[varName];
      }
    } catch (scriptErr) {
      console.warn(`[StoreLoader] Script data/stores/${storeKey}.js não disponível, tentando fetch JSON:`, scriptErr);
    }

    // 4. Fallback para fetch (.json) se estiver rodando em servidor HTTP/HTTPS (Vercel)
    try {
      const resp = await fetch(`./data/stores/${storeKey}.json`);
      if (resp.ok) {
        const data = await resp.json();
        this.cache.stores[storeKey] = data;
        return data;
      }
    } catch (fetchErr) {
      console.warn(`[StoreLoader] Fetch JSON falhou para ${storeKey}:`, fetchErr);
    }

    // 5. Fallback legado para MASTER_PAYLOAD inline se existir
    if (window.MASTER_PAYLOAD && window.MASTER_PAYLOAD.stores && window.MASTER_PAYLOAD.stores[storeKey]) {
      return window.MASTER_PAYLOAD.stores[storeKey];
    }

    throw new Error(`Não foi possível carregar os dados da loja '${storeKey}'.`);
  },

  async loadAnalytics() {
    if (this.cache.analytics) return this.cache.analytics;
    if (window.__STORE_ANALYTICS) {
      this.cache.analytics = window.__STORE_ANALYTICS;
      return window.__STORE_ANALYTICS;
    }

    try {
      await this.loadScript(`data/stores/analytics.js`);
      if (window.__STORE_ANALYTICS) {
        this.cache.analytics = window.__STORE_ANALYTICS;
        return window.__STORE_ANALYTICS;
      }
    } catch (e) {
      // fallback fetch
    }

    try {
      const resp = await fetch('./data/stores/analytics.json');
      if (resp.ok) {
        this.cache.analytics = await resp.json();
        return this.cache.analytics;
      }
    } catch (e) {
      console.warn("[StoreLoader] Falha ao carregar analytics:", e);
    }

    return { history: [], available_csvs: [] };
  },

  async loadMoldes() {
    if (this.cache.moldes) return this.cache.moldes;
    if (window.__STORE_MOLDES) {
      this.cache.moldes = window.__STORE_MOLDES;
      return window.__STORE_MOLDES;
    }

    try {
      await this.loadScript(`data/stores/moldes.js`);
      if (window.__STORE_MOLDES) {
        this.cache.moldes = window.__STORE_MOLDES;
        return window.__STORE_MOLDES;
      }
    } catch (e) {
      // fallback fetch
    }

    try {
      const resp = await fetch('./data/stores/moldes.json');
      if (resp.ok) {
        this.cache.moldes = await resp.json();
        return this.cache.moldes;
      }
    } catch (e) {
      console.warn("[StoreLoader] Falha ao carregar moldes:", e);
    }

    return {};
  }
};
