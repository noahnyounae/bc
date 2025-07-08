#!/bin/bash

# Script de build et test pour ActionChain Token
# Usage: ./build.sh [test|compile|deploy|web]

set -e  # Arrêt sur erreur

PROJECT_DIR="/Users/noahnyounae/Documents/PING/python"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction d'affichage avec couleurs
log_info() {
    echo -e "${BLUE}info  $1${NC}"
}

log_success() {
    echo -e "${GREEN}valid $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}warning  $1${NC}"
}

log_error() {
    echo -e "${RED}error $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "ActionChain Token - Build System"
echo "=================================="
echo -e "${NC}"

# Vérification de l'environnement
check_environment() {
    log_info "Vérification de l'environnement..."
    
    if [ ! -f "$VENV_PYTHON" ]; then
        log_error "Environnement Python virtuel non trouvé"
        exit 1
    fi
    
    # Vérifier SmartPy
    if ! $VENV_PYTHON -c "import smartpy" 2>/dev/null; then
        log_warning "SmartPy non installé, installation en cours..."
        $VENV_PYTHON -m pip install smartpy-cli
    fi
    
    log_success "Environnement vérifié"
}

# Tests du smart contract
run_tests() {
    log_info "Exécution des tests..."
    
    cd "$PROJECT_DIR"
    
    # Test principal
    log_info "Test du contrat principal..."
    $VENV_PYTHON ActionChain.py
    
    # Tests complets
    log_info "Tests complets..."
    $VENV_PYTHON test_complete.py
    
    # Tests de déploiement
    log_info "Tests de déploiement..."
    $VENV_PYTHON deploy.py
    
    log_success "Tous les tests sont passés!"
}

# Compilation du contrat
compile_contract() {
    log_info "Compilation du contrat..."
    
    cd "$PROJECT_DIR"
    
    # Créer le dossier de sortie
    mkdir -p output
    
    # Compiler avec SmartPy
    log_info "Compilation avec SmartPy..."
    $VENV_PYTHON -c "
import smartpy as sp
from ActionChain import main

# Création du contrat pour compilation
admin = sp.test_account('Admin')
contract = main.ActionChainToken(
    admin=admin.address,
    initial_supply=1_000_000,
    token_name='ActionChain Token',
    token_symbol='ACT'
)

# Compilation
scenario = sp.test_scenario('Compilation', main)
scenario += contract

print('Contrat compilé avec succès!')
print(f'Fichiers générés dans: output/')
"
    
    log_success "Compilation terminée"
}

# Lancement du serveur web
start_web_server() {
    log_info "Démarrage du serveur web..."
    
    cd "$PROJECT_DIR/web"
    
    # Vérifier si Node.js est installé
    if ! command -v node &> /dev/null; then
        log_warning "Node.js non trouvé, utilisation de Python pour le serveur"
        $VENV_PYTHON -m http.server 8080
    else
        # Utiliser http-server si disponible
        if command -v http-server &> /dev/null; then
            log_info "Utilisation de http-server"
            http-server . -p 8080
        else
            log_warning "http-server non trouvé, installation..."
            npm install -g http-server
            http-server . -p 8080
        fi
    fi
}

# Déploiement sur testnet
deploy_testnet() {
    log_info "Préparation du déploiement sur testnet..."
    
    cd "$PROJECT_DIR"
    
    # Compilation préalable
    compile_contract
    
    log_warning "Configuration manuelle requise:"
    echo "1. Configurez votre wallet Tezos"
    echo "2. Assurez-vous d'avoir des fonds sur le testnet"
    echo "3. Modifiez les paramètres dans deploy.py si nécessaire"
    echo ""
    echo "Commandes de déploiement:"
    echo "  smartpy deploy output/ --network ghostnet"
    echo "  ou utilisez Taquito CLI pour plus de contrôle"
    
    log_info "Guide de déploiement généré dans deployment_guide.md"
}

# Menu d'aide
show_help() {
    echo "Usage: ./build.sh [commande]"
    echo ""
    echo "Commandes disponibles:"
    echo "  test      - Exécuter tous les tests"
    echo "  compile   - Compiler le contrat SmartPy"
    echo "  deploy    - Préparer le déploiement"
    echo "  web       - Lancer le serveur web de développement"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "Sans argument, exécute: test + compile"
}

# Fonction principale
main() {
    check_environment
    
    case "${1:-default}" in
        "test")
            run_tests
            ;;
        "compile")
            compile_contract
            ;;
        "deploy")
            deploy_testnet
            ;;
        "web")
            start_web_server
            ;;
        "help")
            show_help
            ;;
        "default")
            log_info "Exécution par défaut: tests + compilation"
            run_tests
            compile_contract
            log_success "Build terminé avec succès!"
            ;;
        *)
            log_error "Commande inconnue: $1"
            show_help
            exit 1
            ;;
    esac
}

# Point d'entrée
main "$@"
