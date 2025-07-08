#!/usr/bin/env python3
"""
ActionChain Token - Presentation Generator
Creates a PDF presentation explaining the project, use case, and architecture
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, blue, green, red
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, String
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import tempfile
import os

class ActionChainPresentation:
    def __init__(self):
        self.doc = SimpleDocTemplate(
            "ActionChain_Token_Presentation.pdf",
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Define custom colors
        self.primary_color = HexColor('#2E86AB')
        self.accent_color = HexColor('#A23B72')
        self.success_color = HexColor('#F18F01')
        self.bg_color = HexColor('#F5F5F5')
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=self.primary_color,
            alignment=TA_CENTER
        )
        
        self.section_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=12,
            textColor=self.accent_color,
            leftIndent=0
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        )

    def create_title_page(self):
        """Create the title page"""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph("🔗 ActionChain Token", self.title_style)
        self.story.append(title)
        
        subtitle = Paragraph(
            "Un Système de Trading Décentralisé sur Blockchain Tezos",
            ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=self.accent_color,
                alignment=TA_CENTER,
                spaceAfter=30
            )
        )
        self.story.append(subtitle)
        
        # Project info
        info_text = """
        <b>Token Symbol:</b> ACT<br/>
        <b>Blockchain:</b> Tezos<br/>
        <b>Type:</b> Smart Contract avec Orderbook Intégré<br/>
        <b>Date:</b> Juillet 2025
        """
        info = Paragraph(info_text, self.body_style)
        self.story.append(info)
        
        self.story.append(PageBreak())

    def create_use_case_section(self):
        """Explain the use case and problem being solved"""
        title = Paragraph("1. Cas d'Usage et Problématique", self.section_style)
        self.story.append(title)
        
        problem_text = """
        <b>Problématique Actuelle:</b><br/>
        • Les échanges centralisés contrôlent la liquidité et imposent des frais élevés<br/>
        • Manque de transparence dans l'exécution des ordres<br/>
        • Risques de contrepartie et de censure<br/>
        • Accès limité aux marchés pour les petits investisseurs<br/><br/>
        
        <b>Notre Solution:</b><br/>
        ActionChain Token résout ces problèmes en créant un système de trading entièrement décentralisé
        où les utilisateurs peuvent échanger des tokens directement sur la blockchain Tezos, sans
        intermédiaires centralisés.
        """
        self.story.append(Paragraph(problem_text, self.body_style))
        
        benefits_text = """
        <b>Avantages de notre approche:</b><br/>
        • <b>Décentralisation complète:</b> Aucun point central de défaillance<br/>
        • <b>Transparence totale:</b> Tous les ordres et transactions sont visibles on-chain<br/>
        • <b>Frais réduits:</b> Seulement les frais de gas de la blockchain<br/>
        • <b>Accès global:</b> Ouvert à tous, 24/7<br/>
        • <b>Auto-custody:</b> Les utilisateurs gardent le contrôle de leurs fonds<br/>
        • <b>Résistance à la censure:</b> Impossible de bloquer ou restreindre l'accès
        """
        self.story.append(Paragraph(benefits_text, self.body_style))
        
        self.story.append(PageBreak())

    def create_blockchain_solution_section(self):
        """Explain how blockchain solves the use case"""
        title = Paragraph("2. Comment la Blockchain Résout le Problème", self.section_style)
        self.story.append(title)
        
        blockchain_text = """
        <b>Pourquoi Tezos?</b><br/>
        • <b>Smart Contracts Sécurisés:</b> Michelson offre une vérification formelle<br/>
        • <b>Faibles Coûts:</b> Transactions peu coûteuses comparé à Ethereum<br/>
        • <b>Gouvernance On-Chain:</b> Évolution démocratique du protocole<br/>
        • <b>Proof-of-Stake:</b> Écologique et énergétiquement efficace<br/><br/>
        
        <b>Fonctionnalités Blockchain Exploitées:</b><br/><br/>
        
        <b>1. Immutabilité:</b><br/>
        Tous les ordres et trades sont enregistrés de manière permanente et vérifiable.
        Impossible de modifier rétroactivement l'historique des transactions.<br/><br/>
        
        <b>2. Exécution Automatique:</b><br/>
        Les smart contracts exécutent automatiquement les trades selon des règles
        prédéfinies, sans intervention humaine ni risque de manipulation.<br/><br/>
        
        <b>3. Décentralisation:</b><br/>
        Le carnet d'ordres existe directement sur la blockchain, éliminant le besoin
        d'un serveur central ou d'un intermédiaire de confiance.<br/><br/>
        
        <b>4. Interopérabilité:</b><br/>
        Compatible avec l'écosystème Tezos existant et les autres dApps.
        """
        self.story.append(Paragraph(blockchain_text, self.body_style))
        
        self.story.append(PageBreak())

    def create_features_section(self):
        """Detail the main features"""
        title = Paragraph("3. Fonctionnalités Principales", self.section_style)
        self.story.append(title)
        
        # Create features table
        features_data = [
            ['Fonctionnalité', 'Description', 'Avantage'],
            ['Token Standard', 'Mint, burn, transfer de tokens ACT', 'Gestion flexible de l\'offre'],
            ['Ordres d\'Achat', 'Placement d\'ordres avec paiement en Tez', 'Liquidité buyer-side'],
            ['Ordres de Vente', 'Vente de tokens au prix souhaité', 'Contrôle du prix de vente'],
            ['Matching Automatique', 'Exécution automatique des ordres compatibles', 'Efficacité et rapidité'],
            ['Annulation d\'Ordres', 'Annulation avec remboursement automatique', 'Flexibilité pour les traders'],
            ['Statistiques Live', 'Prix actuel, volume 24h, historique', 'Information transparente'],
            ['Interface Web', 'dApp complète avec graphiques et orderbook', 'Expérience utilisateur intuitive']
        ]
        
        features_table = Table(features_data, colWidths=[1.8*inch, 2.5*inch, 2*inch])
        features_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.story.append(features_table)
        self.story.append(Spacer(1, 20))
        
        # Technical details
        tech_text = """
        <b>Détails Techniques:</b><br/><br/>
        
        <b>• Smart Contract en SmartPy:</b><br/>
        Utilise SmartPy pour une syntaxe Python familière avec compilation vers Michelson<br/><br/>
        
        <b>• Storage Optimisé:</b><br/>
        Big_maps pour les soldes, ordres et trades pour une scalabilité maximale<br/><br/>
        
        <b>• Vues On-Chain:</b><br/>
        Accès en lecture aux données sans frais de transaction<br/><br/>
        
        <b>• Gestion des Erreurs:</b><br/>
        Assertions complètes pour prévenir les états invalides<br/><br/>
        
        <b>• Tests Complets:</b><br/>
        Suite de tests couvrant tous les scénarios d'usage
        """
        self.story.append(Paragraph(tech_text, self.body_style))
        
        self.story.append(PageBreak())

    def create_ui_diagram(self):
        """Create UI mockup diagram"""
        title = Paragraph("4. Interface Utilisateur (dApp)", self.section_style)
        self.story.append(title)
        
        # Create a simple UI mockup using matplotlib
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Header
        header = patches.Rectangle((0.5, 7), 9, 0.8, linewidth=2, 
                                 edgecolor='#2E86AB', facecolor='#2E86AB')
        ax.add_patch(header)
        ax.text(5, 7.4, 'ActionChain Token - Trading Interface', 
                ha='center', va='center', color='white', fontsize=14, weight='bold')
        
        # Price display
        price_box = patches.Rectangle((0.5, 6), 9, 0.8, linewidth=1, 
                                    edgecolor='#A23B72', facecolor='#F5F5F5')
        ax.add_patch(price_box)
        ax.text(2, 6.4, 'Prix Actuel: 1.20 ꜩ', ha='left', va='center', fontsize=12, weight='bold')
        ax.text(8, 6.4, '+0.05 (+4.35%)', ha='right', va='center', color='green', fontsize=12)
        
        # Chart area
        chart_box = patches.Rectangle((0.5, 3.5), 4, 2.3, linewidth=1, 
                                    edgecolor='gray', facecolor='white')
        ax.add_patch(chart_box)
        ax.text(2.5, 5.5, 'Graphique des Prix', ha='center', va='center', fontsize=11, weight='bold')
        ax.text(2.5, 4.5, '📈', ha='center', va='center', fontsize=30)
        
        # Orderbook
        orderbook_box = patches.Rectangle((5, 3.5), 4.5, 2.3, linewidth=1, 
                                        edgecolor='gray', facecolor='white')
        ax.add_patch(orderbook_box)
        ax.text(7.25, 5.5, 'Carnet d\'Ordres', ha='center', va='center', fontsize=11, weight='bold')
        
        # Sell orders
        sell_box = patches.Rectangle((5.2, 4.8), 2, 0.8, linewidth=1, 
                                   edgecolor='red', facecolor='#ffe6e6')
        ax.add_patch(sell_box)
        ax.text(6.2, 5.2, 'Ventes', ha='center', va='center', fontsize=10, color='red')
        
        # Buy orders
        buy_box = patches.Rectangle((7.3, 4.8), 2, 0.8, linewidth=1, 
                                  edgecolor='green', facecolor='#e6ffe6')
        ax.add_patch(buy_box)
        ax.text(8.3, 5.2, 'Achats', ha='center', va='center', fontsize=10, color='green')
        
        # Trading forms
        buy_form = patches.Rectangle((0.5, 0.5), 4, 2.8, linewidth=1, 
                                   edgecolor='green', facecolor='#e6ffe6')
        ax.add_patch(buy_form)
        ax.text(2.5, 2.8, 'Formulaire d\'Achat', ha='center', va='center', fontsize=11, weight='bold')
        ax.text(2.5, 2.2, 'Prix: [____] ꜩ', ha='center', va='center', fontsize=10)
        ax.text(2.5, 1.8, 'Quantité: [____]', ha='center', va='center', fontsize=10)
        ax.text(2.5, 1.4, '[Bouton Acheter]', ha='center', va='center', fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='green', alpha=0.7))
        
        sell_form = patches.Rectangle((5, 0.5), 4.5, 2.8, linewidth=1, 
                                    edgecolor='red', facecolor='#ffe6e6')
        ax.add_patch(sell_form)
        ax.text(7.25, 2.8, 'Formulaire de Vente', ha='center', va='center', fontsize=11, weight='bold')
        ax.text(7.25, 2.2, 'Prix: [____] ꜩ', ha='center', va='center', fontsize=10)
        ax.text(7.25, 1.8, 'Quantité: [____]', ha='center', va='center', fontsize=10)
        ax.text(7.25, 1.4, '[Bouton Vendre]', ha='center', va='center', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='red', alpha=0.7))
        
        plt.title('Interface dApp ActionChain Token', fontsize=16, weight='bold', pad=20)
        
        # Save the plot
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Add to story
        img = Image(buf, width=7*inch, height=5.6*inch)
        self.story.append(img)
        
        ui_description = """
        <b>Composants de l'Interface:</b><br/>
        • <b>Header:</b> Affichage du prix actuel et variation<br/>
        • <b>Graphique:</b> Évolution des prix en temps réel<br/>
        • <b>Carnet d'Ordres:</b> Visualisation des ordres d'achat et de vente<br/>
        • <b>Formulaires de Trading:</b> Interface intuitive pour passer des ordres<br/>
        • <b>Historique:</b> Liste des dernières transactions<br/>
        • <b>Statistiques:</b> Volume 24h, spread, liquidité
        """
        self.story.append(Paragraph(ui_description, self.body_style))
        
        self.story.append(PageBreak())

    def create_architecture_diagram(self):
        """Create system architecture diagram"""
        title = Paragraph("5. Architecture et Interactions On-Chain/Off-Chain", self.section_style)
        self.story.append(title)
        
        # Create architecture diagram
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Blockchain layer (bottom)
        blockchain_rect = patches.Rectangle((1, 0.5), 10, 2, linewidth=3, 
                                          edgecolor='#2E86AB', facecolor='#E3F2FD')
        ax.add_patch(blockchain_rect)
        ax.text(6, 1.5, 'TEZOS BLOCKCHAIN', ha='center', va='center', 
                fontsize=14, weight='bold', color='#2E86AB')
        
        # Smart Contract
        contract_rect = patches.Rectangle((2, 1), 3, 1, linewidth=2, 
                                        edgecolor='#A23B72', facecolor='white')
        ax.add_patch(contract_rect)
        ax.text(3.5, 1.5, 'ActionChain\nSmart Contract', ha='center', va='center', 
                fontsize=10, weight='bold')
        
        # Storage
        storage_rect = patches.Rectangle((7, 1), 3, 1, linewidth=2, 
                                       edgecolor='#F18F01', facecolor='white')
        ax.add_patch(storage_rect)
        ax.text(8.5, 1.5, 'Storage\n(Balances, Orders, Trades)', ha='center', va='center', 
                fontsize=10, weight='bold')
        
        # Web3 Interface layer
        web3_rect = patches.Rectangle((1, 3.5), 10, 1.5, linewidth=2, 
                                    edgecolor='#4CAF50', facecolor='#E8F5E8')
        ax.add_patch(web3_rect)
        ax.text(6, 4.25, 'WEB3 INTERFACE LAYER', ha='center', va='center', 
                fontsize=12, weight='bold', color='#4CAF50')
        
        # Wallet integration
        wallet_rect = patches.Rectangle((2, 3.7), 2.5, 1.1, linewidth=1, 
                                      edgecolor='gray', facecolor='white')
        ax.add_patch(wallet_rect)
        ax.text(3.25, 4.25, 'Temple Wallet\nIntegration', ha='center', va='center', fontsize=9)
        
        # Transaction handling
        tx_rect = patches.Rectangle((7.5, 3.7), 2.5, 1.1, linewidth=1, 
                                  edgecolor='gray', facecolor='white')
        ax.add_patch(tx_rect)
        ax.text(8.75, 4.25, 'Transaction\nSigning & Broadcasting', ha='center', va='center', fontsize=9)
        
        # Frontend layer
        frontend_rect = patches.Rectangle((1, 6), 10, 2, linewidth=2, 
                                        edgecolor='#9C27B0', facecolor='#F3E5F5')
        ax.add_patch(frontend_rect)
        ax.text(6, 7, 'FRONTEND dAPP', ha='center', va='center', 
                fontsize=12, weight='bold', color='#9C27B0')
        
        # UI components
        components = [
            (2.5, 6.3, 'Trading\nInterface'),
            (4.5, 6.3, 'Orderbook\nVisualization'),
            (6.5, 6.3, 'Price\nCharts'),
            (8.5, 6.3, 'Portfolio\nManagement'),
            (10.5, 6.3, 'Transaction\nHistory')
        ]
        
        for x, y, label in components:
            comp_rect = patches.Rectangle((x-0.4, y), 0.8, 1.4, linewidth=1, 
                                        edgecolor='gray', facecolor='white')
            ax.add_patch(comp_rect)
            ax.text(x, y+0.7, label, ha='center', va='center', fontsize=8)
        
        # User layer
        user_rect = patches.Rectangle((3, 8.5), 6, 1, linewidth=2, 
                                    edgecolor='#FF5722', facecolor='#FFF3E0')
        ax.add_patch(user_rect)
        ax.text(6, 9, 'UTILISATEURS (TRADERS)', ha='center', va='center', 
                fontsize=12, weight='bold', color='#FF5722')
        
        # Arrows showing data flow
        # User to Frontend
        ax.annotate('', xy=(6, 8), xytext=(6, 8.5), 
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        
        # Frontend to Web3
        ax.annotate('', xy=(6, 5), xytext=(6, 6), 
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        
        # Web3 to Blockchain
        ax.annotate('', xy=(6, 2.5), xytext=(6, 3.5), 
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        
        # Contract to Storage
        ax.annotate('', xy=(7, 1.5), xytext=(5, 1.5), 
                   arrowprops=dict(arrowstyle='<->', color='black', lw=2))
        
        # Add labels for interactions
        ax.text(6.3, 8.25, 'Interactions\nUtilisateur', ha='left', va='center', fontsize=8, 
                bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
        
        ax.text(6.3, 5.5, 'Appels Web3\nTezTalks JS', ha='left', va='center', fontsize=8,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='lightblue', alpha=0.7))
        
        ax.text(6.3, 3, 'Transactions\nBlockchain', ha='left', va='center', fontsize=8,
                bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgreen', alpha=0.7))
        
        plt.title('Architecture Système ActionChain Token', fontsize=16, weight='bold', pad=20)
        
        # Save the plot
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Add to story
        img = Image(buf, width=8*inch, height=6.7*inch)
        self.story.append(img)
        
        # Architecture explanation
        arch_text = """
        <b>Flux de Données et Interactions:</b><br/><br/>
        
        <b>1. Couche Utilisateur:</b><br/>
        Les traders interagissent avec l'interface web pour passer des ordres, consulter
        le carnet d'ordres et suivre leurs positions.<br/><br/>
        
        <b>2. Frontend dApp:</b><br/>
        Interface React/JavaScript qui gère l'affichage des données, la validation des
        formulaires et la préparation des transactions.<br/><br/>
        
        <b>3. Couche Web3:</b><br/>
        Intégration avec Temple Wallet pour la signature des transactions et l'interaction
        avec la blockchain Tezos via TezTalks.js.<br/><br/>
        
        <b>4. Smart Contract:</b><br/>
        Logique métier centralisée qui gère les ordres, exécute les trades et maintient
        l'état du système de manière décentralisée.<br/><br/>
        
        <b>5. Storage On-Chain:</b><br/>
        Toutes les données critiques (soldes, ordres, historique) sont stockées
        directement sur la blockchain pour garantir la transparence et la persistance.
        """
        self.story.append(Paragraph(arch_text, self.body_style))
        
        self.story.append(PageBreak())

    def create_benefits_conclusion(self):
        """Create benefits and conclusion section"""
        title = Paragraph("6. Avantages Concurrentiels et Vision", self.section_style)
        self.story.append(title)
        
        benefits_text = """
        <b>Avantages Uniques d'ActionChain Token:</b><br/><br/>
        
        <b>• Véritable Décentralisation:</b><br/>
        Contrairement aux DEX traditionnels qui utilisent des relayers centralisés,
        ActionChain intègre le carnet d'ordres directement dans le smart contract.<br/><br/>
        
        <b>• Coûts Réduits:</b><br/>
        Élimination des frais d'intermédiaires, seuls les frais de gas s'appliquent.<br/><br/>
        
        <b>• Transparence Totale:</b><br/>
        Tous les ordres et trades sont visibles et vérifiables publiquement.<br/><br/>
        
        <b>• Résistance à la Censure:</b><br/>
        Impossible de bloquer ou restreindre l'accès aux marchés.<br/><br/>
        
        <b>• Composabilité:</b><br/>
        Intégration facile avec d'autres protocoles DeFi de l'écosystème Tezos.<br/><br/>
        
        <b>Vision Future:</b><br/>
        • Extension à d'autres types d'actifs (NFTs, stablecoins)<br/>
        • Intégration de fonctionnalités DeFi avancées (lending, yield farming)<br/>
        • Gouvernance décentralisée par les détenteurs de tokens ACT<br/>
        • Expansion multi-chaînes via des bridges interopérables<br/><br/>
        
        <b>Impact Attendu:</b><br/>
        ActionChain Token représente une étape importante vers la démocratisation
        de la finance décentralisée, offrant aux utilisateurs un contrôle total
        sur leurs actifs et leurs transactions.
        """
        self.story.append(Paragraph(benefits_text, self.body_style))
        
        # Final summary box
        summary_data = [
            ['Métrique', 'Valeur'],
            ['Type de Projet', 'DEX avec Orderbook On-Chain'],
            ['Blockchain', 'Tezos'],
            ['Langage Smart Contract', 'SmartPy (Michelson)'],
            ['Frontend', 'HTML/CSS/JavaScript + Web3'],
            ['Cas d\'Usage Principal', 'Trading Décentralisé'],
            ['Public Cible', 'Traders DeFi et Investisseurs Crypto'],
            ['Avantage Concurrentiel', 'Véritable Décentralisation']
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.bg_color),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        self.story.append(Spacer(1, 20))
        self.story.append(summary_table)

    def generate_pdf(self):
        """Generate the complete PDF presentation"""
        print("Generating ActionChain Token presentation...")
        
        self.create_title_page()
        self.create_use_case_section()
        self.create_blockchain_solution_section()
        self.create_features_section()
        self.create_ui_diagram()
        self.create_architecture_diagram()
        self.create_benefits_conclusion()
        
        # Build the PDF
        self.doc.build(self.story)
        print("✅ Presentation generated: ActionChain_Token_Presentation.pdf")

if __name__ == "__main__":
    presentation = ActionChainPresentation()
    presentation.generate_pdf()
