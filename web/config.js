// Configuration ActionChain Token

const CONFIG = {
    // Adresse du contrat (à mettre à jour après déploiement)
    CONTRACT_ADDRESS: 'KT1...', // Remplacer par l'adresse réelle après déploiement
    
    // Configuration réseau
    NETWORK: {
        name: 'ghostnet',  // ou 'mainnet' pour la production
        rpc: 'https://ghostnet.smartpy.io'
    },
    
    // Paramètres du token
    TOKEN: {
        name: 'ActionChain Token',
        symbol: 'ACT',
        decimals: 6
    },
    
    // Limites et contraintes
    LIMITS: {
        minOrderQuantity: 1,
        maxOrderQuantity: 1000000,
        minPrice: 0.01,  // 0.01 tez
        maxPrice: 1000,  // 1000 tez
        priceDecimals: 2 // Maximum 2 décimales
    },
    
    // Interface utilisateur
    UI: {
        refreshInterval: 5000,  // 5 secondes
        chartUpdateInterval: 30000,  // 30 secondes
        maxOrderbookOrders: 10,
        maxTradeHistory: 50
    }
};

// Export de la configuration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else {
    window.ACTIONCHAIN_CONFIG = CONFIG;
}
