// Configuration du contrat
const CONTRACT_ADDRESS = 'KT1...'; // Adresse du contrat déployé
const RPC_URL = 'https://mainnet-tezos.giganode.io'; // RPC Tezos

// Variables globales
let tezos = null;
let userAddress = null;
let contractInstance = null;
let priceChart = null;

// Données de démonstration (à remplacer par les vraies données du contrat)
let mockData = {
    currentPrice: 1.20,
    priceChange: 0.05,
    priceChangePercent: 4.35,
    volume24h: 15432,
    highPrice: 1.25,
    lowPrice: 1.15,
    totalSupply: 1000000,
    circulatingSupply: 750000,
    marketCap: 900000,
    
    buyOrders: [
        { price: 1.21, quantity: 150, total: 181.5 },
        { price: 1.20, quantity: 300, total: 360 },
        { price: 1.19, quantity: 200, total: 238 },
        { price: 1.18, quantity: 500, total: 590 },
        { price: 1.17, quantity: 100, total: 117 }
    ],
    
    sellOrders: [
        { price: 1.22, quantity: 100, total: 122 },
        { price: 1.23, quantity: 250, total: 307.5 },
        { price: 1.24, quantity: 180, total: 223.2 },
        { price: 1.25, quantity: 400, total: 500 },
        { price: 1.26, quantity: 75, total: 94.5 }
    ],
    
    tradeHistory: [
        { time: '14:32:15', type: 'buy', price: 1.20, quantity: 50, total: 60 },
        { time: '14:31:42', type: 'sell', price: 1.19, quantity: 100, total: 119 },
        { time: '14:30:18', type: 'buy', price: 1.21, quantity: 75, total: 90.75 },
        { time: '14:29:33', type: 'sell', price: 1.18, quantity: 200, total: 236 },
        { time: '14:28:47', type: 'buy', price: 1.22, quantity: 25, total: 30.5 }
    ],
    
    userBalance: {
        act: 0,
        xtz: 0
    }
};

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    console.log('ActionChain Token Interface chargée');
    
    initializeChart();
    updateUI();
    setupEventListeners();
    
    // Simulation de mise à jour en temps réel
    setInterval(updateMarketData, 5000);
});

// Configuration du graphique
function initializeChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Données de prix historiques (simulation)
    const priceData = generateMockPriceData();
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: priceData.labels,
            datasets: [{
                label: 'Prix ACT (ꜩ)',
                data: priceData.prices,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Temps',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Prix (ꜩ)',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

// Génération de données de prix de démonstration
function generateMockPriceData() {
    const labels = [];
    const prices = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        labels.push(time.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
        
        // Simulation de prix avec variation aléatoire
        const basePrice = 1.20;
        const variation = (Math.random() - 0.5) * 0.1;
        prices.push((basePrice + variation).toFixed(2));
    }
    
    return { labels, prices };
}

// Configuration des événements
function setupEventListeners() {
    // Calcul automatique des totaux
    document.getElementById('buyPrice').addEventListener('input', calculateBuyTotal);
    document.getElementById('buyQuantity').addEventListener('input', calculateBuyTotal);
    document.getElementById('sellPrice').addEventListener('input', calculateSellTotal);
    document.getElementById('sellQuantity').addEventListener('input', calculateSellTotal);
    
    // Formulaires de trading
    document.getElementById('buyForm').addEventListener('submit', handleBuyOrder);
    document.getElementById('sellForm').addEventListener('submit', handleSellOrder);
    
    // Wallet
    document.getElementById('connectWallet').addEventListener('click', connectWallet);
    document.getElementById('refreshBalance').addEventListener('click', refreshBalance);
}

// Calculs des totaux
function calculateBuyTotal() {
    const price = parseFloat(document.getElementById('buyPrice').value) || 0;
    const quantity = parseInt(document.getElementById('buyQuantity').value) || 0;
    const total = (price * quantity).toFixed(2);
    document.getElementById('buyTotal').textContent = `${total} ꜩ`;
}

function calculateSellTotal() {
    const price = parseFloat(document.getElementById('sellPrice').value) || 0;
    const quantity = parseInt(document.getElementById('sellQuantity').value) || 0;
    const total = (price * quantity).toFixed(2);
    document.getElementById('sellTotal').textContent = `${total} ꜩ`;
}

// Gestion des ordres d'achat
async function handleBuyOrder(event) {
    event.preventDefault();
    
    const price = parseFloat(document.getElementById('buyPrice').value);
    const quantity = parseInt(document.getElementById('buyQuantity').value);
    
    if (!price || !quantity) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    if (!userAddress) {
        alert('Veuillez connecter votre wallet');
        return;
    }
    
    try {
        // Vérification que le prix a maximum 2 décimales
        if (!isValidPrice(price)) {
            alert('Le prix doit avoir maximum 2 décimales');
            return;
        }
        
        const priceInMutez = Math.round(price * 1000000); // Conversion en mutez
        const totalAmount = Math.round(price * quantity * 1000000); // Total en mutez
        
        console.log(`Placement d'un ordre d'achat: ${quantity} ACT à ${price} ꜩ`);
        
        // Simulation de l'appel au contrat
        await simulateContractCall('place_buy_order', {
            price: priceInMutez,
            quantity: quantity
        }, totalAmount);
        
        alert(`Ordre d'achat placé: ${quantity} ACT à ${price} ꜩ`);
        
        // Reset du formulaire
        document.getElementById('buyForm').reset();
        calculateBuyTotal();
        
        // Mise à jour de l'interface
        updateOrderbook();
        
    } catch (error) {
        console.error('Erreur lors du placement de l\'ordre d\'achat:', error);
        alert('Erreur lors du placement de l\'ordre');
    }
}

// Gestion des ordres de vente
async function handleSellOrder(event) {
    event.preventDefault();
    
    const price = parseFloat(document.getElementById('sellPrice').value);
    const quantity = parseInt(document.getElementById('sellQuantity').value);
    
    if (!price || !quantity) {
        alert('Veuillez remplir tous les champs');
        return;
    }
    
    if (!userAddress) {
        alert('Veuillez connecter votre wallet');
        return;
    }
    
    try {
        // Vérification que le prix a maximum 2 décimales
        if (!isValidPrice(price)) {
            alert('Le prix doit avoir maximum 2 décimales');
            return;
        }
        
        // Vérification du solde
        if (mockData.userBalance.act < quantity) {
            alert('Solde insuffisant en tokens ACT');
            return;
        }
        
        const priceInMutez = Math.round(price * 1000000); // Conversion en mutez
        
        console.log(`Placement d'un ordre de vente: ${quantity} ACT à ${price} ꜩ`);
        
        // Simulation de l'appel au contrat
        await simulateContractCall('place_sell_order', {
            price: priceInMutez,
            quantity: quantity
        }, 0);
        
        alert(`Ordre de vente placé: ${quantity} ACT à ${price} ꜩ`);
        
        // Reset du formulaire
        document.getElementById('sellForm').reset();
        calculateSellTotal();
        
        // Mise à jour de l'interface
        updateOrderbook();
        
    } catch (error) {
        console.error('Erreur lors du placement de l\'ordre de vente:', error);
        alert('Erreur lors du placement de l\'ordre');
    }
}

// Validation du prix (max 2 décimales)
function isValidPrice(price) {
    const priceStr = price.toString();
    const decimalIndex = priceStr.indexOf('.');
    
    if (decimalIndex === -1) return true; // Pas de décimales
    
    const decimals = priceStr.substring(decimalIndex + 1);
    return decimals.length <= 2;
}

// Simulation d'appel au contrat
async function simulateContractCall(method, params, amount) {
    console.log(`Appel simulé au contrat: ${method}`, params, `Montant: ${amount} mutez`);
    
    // Simulation d'un délai réseau
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Simulation d'une réponse positive (en réalité, ici on appellerait le vrai contrat)
    return { success: true };
}

// Connexion du wallet
async function connectWallet() {
    try {
        console.log('Tentative de connexion au wallet...');
        
        // Simulation de connexion (à remplacer par la vraie implémentation Tezos)
        userAddress = 'tz1...SimulatedAddress';
        
        // Mise à jour de l'interface
        document.getElementById('connectWallet').textContent = 'Connecté';
        document.getElementById('connectWallet').disabled = true;
        document.getElementById('refreshBalance').disabled = false;
        
        // Simulation de soldes
        mockData.userBalance.act = 1000;
        mockData.userBalance.xtz = 5.50;
        
        updateWalletInfo();
        
        alert('Wallet connecté avec succès!');
        
    } catch (error) {
        console.error('Erreur de connexion au wallet:', error);
        alert('Erreur de connexion au wallet');
    }
}

// Actualisation du solde
async function refreshBalance() {
    if (!userAddress) return;
    
    try {
        console.log('Actualisation du solde...');
        
        // Ici on appellerait les vues du contrat pour récupérer les vrais soldes
        // const actBalance = await contractInstance.views.get_balance(userAddress).read();
        // const xtzBalance = await tezos.tz.getBalance(userAddress);
        
        updateWalletInfo();
        alert('Solde actualisé');
        
    } catch (error) {
        console.error('Erreur lors de l\'actualisation:', error);
        alert('Erreur lors de l\'actualisation');
    }
}

// Mise à jour de l'interface utilisateur
function updateUI() {
    updatePriceDisplay();
    updateMarketStats();
    updateOrderbook();
    updateTradeHistory();
    updateWalletInfo();
}

// Mise à jour de l'affichage des prix
function updatePriceDisplay() {
    document.querySelector('.current-price').textContent = `${mockData.currentPrice.toFixed(2)} ꜩ`;
    
    const changeElement = document.querySelector('.price-change');
    const changeText = `${mockData.priceChange >= 0 ? '+' : ''}${mockData.priceChange.toFixed(2)} (${mockData.priceChangePercent >= 0 ? '+' : ''}${mockData.priceChangePercent.toFixed(2)}%)`;
    changeElement.textContent = changeText;
    changeElement.className = `price-change ${mockData.priceChange >= 0 ? 'positive' : 'negative'}`;
}

// Mise à jour des statistiques du marché
function updateMarketStats() {
    document.getElementById('volume24h').textContent = `${mockData.volume24h.toLocaleString()} ACT`;
    document.getElementById('highPrice').textContent = `${mockData.highPrice.toFixed(2)} ꜩ`;
    document.getElementById('lowPrice').textContent = `${mockData.lowPrice.toFixed(2)} ꜩ`;
    document.getElementById('totalSupply').textContent = `${mockData.totalSupply.toLocaleString()} ACT`;
    document.getElementById('circulatingSupply').textContent = `${mockData.circulatingSupply.toLocaleString()} ACT`;
    document.getElementById('marketCap').textContent = `${mockData.marketCap.toLocaleString()} ꜩ`;
}

// Mise à jour du carnet d'ordres
function updateOrderbook() {
    // Ordres de vente (triés par prix croissant)
    const sellOrdersList = document.getElementById('sellOrdersList');
    sellOrdersList.innerHTML = '';
    
    mockData.sellOrders.sort((a, b) => a.price - b.price).forEach(order => {
        const orderElement = document.createElement('div');
        orderElement.className = 'order-item';
        orderElement.innerHTML = `
            <span>${order.price.toFixed(2)}</span>
            <span>${order.quantity}</span>
            <span>${order.total.toFixed(2)}</span>
        `;
        sellOrdersList.appendChild(orderElement);
    });
    
    // Ordres d'achat (triés par prix décroissant)
    const buyOrdersList = document.getElementById('buyOrdersList');
    buyOrdersList.innerHTML = '';
    
    mockData.buyOrders.sort((a, b) => b.price - a.price).forEach(order => {
        const orderElement = document.createElement('div');
        orderElement.className = 'order-item';
        orderElement.innerHTML = `
            <span>${order.price.toFixed(2)}</span>
            <span>${order.quantity}</span>
            <span>${order.total.toFixed(2)}</span>
        `;
        buyOrdersList.appendChild(orderElement);
    });
    
    // Calcul et affichage du spread
    const bestSell = Math.min(...mockData.sellOrders.map(o => o.price));
    const bestBuy = Math.max(...mockData.buyOrders.map(o => o.price));
    const spread = bestSell - bestBuy;
    document.querySelector('.spread').textContent = `Spread: ${spread.toFixed(2)} ꜩ`;
}

// Mise à jour de l'historique des trades
function updateTradeHistory() {
    const tradeHistoryList = document.getElementById('tradeHistoryList');
    tradeHistoryList.innerHTML = '';
    
    mockData.tradeHistory.forEach(trade => {
        const tradeElement = document.createElement('div');
        tradeElement.className = `trade-item ${trade.type}`;
        tradeElement.innerHTML = `
            <span>${trade.time}</span>
            <span class="${trade.type === 'buy' ? 'buy' : 'sell'}">${trade.type === 'buy' ? 'Achat' : 'Vente'}</span>
            <span>${trade.price.toFixed(2)}</span>
            <span>${trade.quantity}</span>
            <span>${trade.total.toFixed(2)}</span>
        `;
        tradeHistoryList.appendChild(tradeElement);
    });
}

// Mise à jour des informations du wallet
function updateWalletInfo() {
    document.getElementById('actBalance').textContent = `${mockData.userBalance.act.toLocaleString()} ACT`;
    document.getElementById('xtzBalance').textContent = `${mockData.userBalance.xtz.toFixed(2)} ꜩ`;
    
    const totalValue = (mockData.userBalance.act * mockData.currentPrice) + mockData.userBalance.xtz;
    document.getElementById('totalValue').textContent = `${totalValue.toFixed(2)} ꜩ`;
}

// Simulation de mise à jour du marché
function updateMarketData() {
    // Petites variations aléatoires du prix
    const variation = (Math.random() - 0.5) * 0.02;
    mockData.currentPrice = Math.max(0.01, mockData.currentPrice + variation);
    
    // Mise à jour du changement de prix
    mockData.priceChange = mockData.currentPrice - 1.20; // Prix de référence
    mockData.priceChangePercent = (mockData.priceChange / 1.20) * 100;
    
    // Mise à jour des prix min/max
    mockData.highPrice = Math.max(mockData.highPrice, mockData.currentPrice);
    mockData.lowPrice = Math.min(mockData.lowPrice, mockData.currentPrice);
    
    // Mise à jour de l'interface
    updatePriceDisplay();
    
    // Mise à jour du graphique
    if (priceChart) {
        const now = new Date();
        const timeLabel = now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
        
        // Ajouter le nouveau point
        priceChart.data.labels.push(timeLabel);
        priceChart.data.datasets[0].data.push(mockData.currentPrice.toFixed(2));
        
        // Garder seulement les 24 derniers points
        if (priceChart.data.labels.length > 24) {
            priceChart.data.labels.shift();
            priceChart.data.datasets[0].data.shift();
        }
        
        priceChart.update('none'); // Animation désactivée pour les mises à jour en temps réel
    }
}

// Utilitaires
function formatNumber(num) {
    return num.toLocaleString('fr-FR');
}

function formatPrice(price) {
    return `${price.toFixed(2)} ꜩ`;
}

// Export pour utilisation dans d'autres modules
window.ActionChainApp = {
    updateMarketData,
    connectWallet,
    refreshBalance
};
