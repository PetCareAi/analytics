// dashboard-clientes.js - Sistema elegante de dashboard para análise de clientes

// Configuração principal do dashboard
const DashboardConfig = {
  title: "Análise Avançada de Clientes",
  theme: "light", // light ou dark
  refreshInterval: 300000, // atualização a cada 5 minutos
  animationDuration: 800,
  colors: {
    primary: ["#2E5BFF", "#3E6FFF", "#5480FF", "#6A91FF", "#80A2FF"],
    secondary: ["#FF6B6B", "#FF8585", "#FFA0A0", "#FFBABA", "#FFD4D4"],
    neutral: ["#2D3748", "#4A5568", "#718096", "#A0AEC0", "#CBD5E0"],
    success: "#10B981",
    warning: "#FBBF24",
    danger: "#EF4444",
    background: "#F9FAFB",
    cardBackground: "#FFFFFF",
    text: "#1E293B",
    lightText: "#64748B"
  },
  layout: {
    gridGap: "20px",
    cardRadius: "12px",
    cardShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
  }
};

// Classe principal do Dashboard
class ClientDashboard {
  constructor(containerId, config = DashboardConfig) {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      throw new Error(`Container with id ${containerId} not found.`);
    }
    
    this.config = config;
    this.charts = {};
    this.data = null;
    this.filteredData = null;
    this.filters = {
      dateRange: 'all',
      segment: 'all',
      region: 'all'
    };
    
    this.initialize();
  }
  
  // Inicialização do dashboard
  async initialize() {
    this.setupTheme();
    this.createLayout();
    this.createLoadingIndicator();
    
    try {
      await this.loadData();
      this.hideLoadingIndicator();
      this.createDashboard();
      this.setupEventListeners();
      this.startAutoRefresh();
    } catch (error) {
      this.showError(`Falha ao carregar dados: ${error.message}`);
      console.error("Dashboard initialization error:", error);
    }
  }
  
  // Configuração de tema (claro/escuro)
  setupTheme() {
    const isDark = this.config.theme === 'dark';
    
    if (isDark) {
      this.config.colors.background = "#1A202C";
      this.config.colors.cardBackground = "#2D3748";
      this.config.colors.text = "#F7FAFC";
      this.config.colors.lightText = "#A0AEC0";
      document.body.classList.add('dark-theme');
    }
    
    // Aplicando CSS de tema
    const style = document.createElement('style');
    style.textContent = `
      :root {
        --color-primary: ${this.config.colors.primary[0]};
        --color-secondary: ${this.config.colors.secondary[0]};
        --color-success: ${this.config.colors.success};
        --color-warning: ${this.config.colors.warning};
        --color-danger: ${this.config.colors.danger};
        --color-background: ${this.config.colors.background};
        --color-card-bg: ${this.config.colors.cardBackground};
        --color-text: ${this.config.colors.text};
        --color-light-text: ${this.config.colors.lightText};
        --grid-gap: ${this.config.layout.gridGap};
        --card-radius: ${this.config.layout.cardRadius};
        --card-shadow: ${this.config.layout.cardShadow};
      }
      
      body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
        background-color: var(--color-background);
        color: var(--color-text);
        margin: 0;
        padding: 0;
        transition: background-color 0.3s, color 0.3s;
      }
      
      .dashboard-container {
        max-width: 1600px;
        margin: 0 auto;
        padding: 24px;
      }
      
      .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
      }
      
      .dashboard-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--color-text);
        margin: 0;
      }
      
      .dashboard-controls {
        display: flex;
        gap: 16px;
      }
      
      .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        grid-auto-rows: minmax(100px, auto);
        gap: var(--grid-gap);
      }
      
      .dashboard-card {
        background-color: var(--color-card-bg);
        border-radius: var(--card-radius);
        box-shadow: var(--card-shadow);
        padding: 20px;
        display: flex;
        flex-direction: column;
        transition: transform 0.2s, box-shadow 0.2s;
      }
      
      .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      }
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
      }
      
      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--color-text);
        margin: 0;
      }
      
      .card-content {
        flex: 1;
        position: relative;
      }
      
      .kpi-card {
        text-align: center;
      }
      
      .kpi-value {
        font-size: 28px;
        font-weight: 700;
        margin: 10px 0;
        color: var(--color-primary);
      }
      
      .kpi-label {
        font-size: 14px;
        color: var(--color-light-text);
      }
      
      .kpi-change {
        font-size: 12px;
        margin-top: 4px;
      }
      
      .kpi-positive {
        color: var(--color-success);
      }
      
      .kpi-negative {
        color: var(--color-danger);
      }
      
      .filter-container {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 20px;
      }
      
      .filter-select {
        background-color: var(--color-card-bg);
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: var(--color-text);
        padding: 8px 12px;
        font-size: 14px;
        cursor: pointer;
      }
      
      .filter-select:focus {
        outline: none;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
      }
      
      .loading-indicator {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
      }
      
      .dark-theme .loading-indicator {
        background-color: rgba(26, 32, 44, 0.7);
      }
      
      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-left-color: var(--color-primary);
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .error-message {
        background-color: #FEE2E2;
        border-left: 4px solid var(--color-danger);
        color: #7F1D1D;
        padding: 16px;
        margin: 20px 0;
        border-radius: 4px;
      }
      
      .dark-theme .error-message {
        background-color: #4A1B1B;
        color: #FCA5A5;
      }
      
      .chart-legend {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-top: 12px;
      }
      
      .legend-item {
        display: flex;
        align-items: center;
        font-size: 12px;
      }
      
      .legend-color {
        width: 12px;
        height: 12px;
        border-radius: 2px;
        margin-right: 4px;
      }
      
      /* Design responsivo */
      @media (max-width: 1200px) {
        .dashboard-grid {
          grid-template-columns: repeat(6, 1fr);
        }
      }
      
      @media (max-width: 768px) {
        .dashboard-grid {
          grid-template-columns: repeat(2, 1fr);
        }
        
        .dashboard-header {
          flex-direction: column;
          align-items: flex-start;
          gap: 16px;
        }
        
        .dashboard-controls {
          width: 100%;
          flex-wrap: wrap;
        }
      }
      
      @media (max-width: 480px) {
        .dashboard-grid {
          grid-template-columns: 1fr;
        }
        
        .dashboard-card {
          padding: 16px;
        }
      }
    `;
    
    document.head.appendChild(style);
  }
  
  // Criação do layout básico
  createLayout() {
    this.container.innerHTML = `
      <div class="dashboard-container">
        <header class="dashboard-header">
          <h1 class="dashboard-title">${this.config.title}</h1>
          <div class="dashboard-controls">
            <button id="export-pdf" class="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Exportar PDF
            </button>
            <button id="theme-toggle" class="action-button">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
              </svg>
              Alternar Tema
            </button>
          </div>
        </header>
        
        <div class="filter-container">
          <select id="date-range-filter" class="filter-select">
            <option value="all">Período: Todos</option>
            <option value="30">Últimos 30 dias</option>
            <option value="90">Últimos 90 dias</option>
            <option value="365">Último ano</option>
          </select>
          
          <select id="segment-filter" class="filter-select">
            <option value="all">Segmento: Todos</option>
            <option value="premium">Premium</option>
            <option value="standard">Standard</option>
            <option value="basic">Básico</option>
          </select>
          
          <select id="region-filter" class="filter-select">
            <option value="all">Região: Todas</option>
            <option value="norte">Norte</option>
            <option value="nordeste">Nordeste</option>
            <option value="centro-oeste">Centro-Oeste</option>
            <option value="sudeste">Sudeste</option>
            <option value="sul">Sul</option>
          </select>
        </div>
        
        <div class="dashboard-grid" id="dashboard-grid">
          <!-- Cards serão inseridos aqui dinamicamente -->
        </div>
      </div>
    `;
    
    // Adicionar CSS para os botões de ação
    const actionButtonStyle = document.createElement('style');
    actionButtonStyle.textContent = `
      .action-button {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background-color: var(--color-card-bg);
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        color: var(--color-text);
        font-size: 14px;
        cursor: pointer;
        transition: background-color 0.2s;
      }
      
      .action-button:hover {
        background-color: ${this.config.theme === 'dark' ? '#4A5568' : '#EDF2F7'};
      }
      
      .action-button svg {
        width: 16px;
        height: 16px;
      }
    `;
    document.head.appendChild(actionButtonStyle);
  }
  
  // Indicador de carregamento
  createLoadingIndicator() {
    this.loadingIndicator = document.createElement('div');
    this.loadingIndicator.className = 'loading-indicator';
    this.loadingIndicator.innerHTML = '<div class="spinner"></div>';
    this.container.appendChild(this.loadingIndicator);
  }
  
  hideLoadingIndicator() {
    this.loadingIndicator.style.display = 'none';
  }
  
  showLoadingIndicator() {
    this.loadingIndicator.style.display = 'flex';
  }
  
  // Exibição de erro
  showError(message) {
    this.hideLoadingIndicator();
    
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    
    const grid = document.getElementById('dashboard-grid');
    grid.innerHTML = '';
    grid.appendChild(errorElement);
  }
  
  // Carregamento de dados (simulado, substituir por sua fonte de dados real)
  async loadData() {
    // Simulando carregamento de dados
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Esta função seria substituída por uma chamada real para carregar dados
    // Por exemplo: fetch('/api/client-data') ou integração com uma API de BI
    
    // Gerando dados de exemplo para demonstração
    this.data = this.generateMockData();
    this.filteredData = this.data;
    
    return this.data;
  }
  
  // Gera dados de exemplo para demonstração
  generateMockData() {
    const regions = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
    const segments = ['Premium', 'Standard', 'Básico'];
    const status = ['Ativo', 'Inativo', 'Pendente'];
    const products = ['Produto A', 'Produto B', 'Produto C', 'Produto D', 'Produto E'];
    
    // Gerar dados de clientes
    const clients = [];
    const now = new Date();
    const recentDate = new Date();
    recentDate.setFullYear(now.getFullYear() - 1);
    
    for (let i = 1; i <= 500; i++) {
      const registrationDate = new Date(
        recentDate.getTime() + Math.random() * (now.getTime() - recentDate.getTime())
      );
      
      const segment = segments[Math.floor(Math.random() * segments.length)];
      let lifetimeValue;
      
      if (segment === 'Premium') {
        lifetimeValue = 5000 + Math.random() * 45000;
      } else if (segment === 'Standard') {
        lifetimeValue = 1000 + Math.random() * 9000;
      } else {
        lifetimeValue = 100 + Math.random() * 1900;
      }
      
      const lastPurchaseDate = new Date(
        registrationDate.getTime() + Math.random() * (now.getTime() - registrationDate.getTime())
      );
      
      // Simular frequência de compra com base no segmento
      let purchaseFrequency;
      if (segment === 'Premium') {
        purchaseFrequency = 1 + Math.random() * 2; // 1-3 compras por mês
      } else if (segment === 'Standard') {
        purchaseFrequency = 0.5 + Math.random() * 1; // 0.5-1.5 compras por mês
      } else {
        purchaseFrequency = 0.1 + Math.random() * 0.4; // 0.1-0.5 compras por mês
      }
      
      // Gerar histórico de compras
      const purchases = [];
      let purchaseDate = new Date(registrationDate);
      let totalSpent = 0;
      
      while (purchaseDate < now) {
        // Adicionar dias baseado na frequência (convertendo frequência mensal para dias)
        const daysToAdd = Math.floor(30 / purchaseFrequency) + Math.floor(Math.random() * 10) - 5;
        purchaseDate = new Date(purchaseDate.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
        
        if (purchaseDate > now) break;
        
        const product = products[Math.floor(Math.random() * products.length)];
        const quantity = Math.floor(Math.random() * 5) + 1;
        let price;
        
        if (segment === 'Premium') {
          price = 150 + Math.random() * 850;
        } else if (segment === 'Standard') {
          price = 50 + Math.random() * 200;
        } else {
          price = 10 + Math.random() * 90;
        }
        
        const purchaseTotal = price * quantity;
        totalSpent += purchaseTotal;
        
        purchases.push({
          date: new Date(purchaseDate),
          product,
          quantity,
          price,
          total: purchaseTotal
        });
      }
      
      const client = {
        id: `CLI${String(i).padStart(6, '0')}`,
        name: `Cliente ${i}`,
        email: `cliente${i}@exemplo.com`,
        phone: `(${Math.floor(Math.random() * 90) + 10}) ${Math.floor(Math.random() * 90000) + 10000}-${Math.floor(Math.random() * 9000) + 1000}`,
        registrationDate,
        segment,
        status: status[Math.floor(Math.random() * status.length)],
        region: regions[Math.floor(Math.random() * regions.length)],
        city: `Cidade ${Math.floor(Math.random() * 100) + 1}`,
        lifetimeValue,
        lastPurchaseDate,
        purchaseFrequency,
        totalPurchases: purchases.length,
        totalSpent,
        purchases,
        satisfaction: Math.floor(Math.random() * 5) + 1, // 1-5 estrelas
        churnRisk: Math.random(),
        loyaltyPoints: Math.floor(Math.random() * 10000),
        hasAppInstalled: Math.random() > 0.5,
        preferredChannel: ['Email', 'SMS', 'App', 'WhatsApp'][Math.floor(Math.random() * 4)],
        ageGroup: ['18-24', '25-34', '35-44', '45-54', '55+'][Math.floor(Math.random() * 5)]
      };
      
      clients.push(client);
    }
    
    // Calcular métricas para o dashboard
    const totalRevenue = clients.reduce((sum, client) => sum + client.totalSpent, 0);
    const totalClients = clients.length;
    const activeClients = clients.filter(client => client.status === 'Ativo').length;
    const averageOrderValue = totalRevenue / clients.reduce((sum, client) => sum + client.totalPurchases, 0);
    
    return {
      clients,
      metrics: {
        totalRevenue,
        totalClients,
        activeClients,
        inactiveRate: (totalClients - activeClients) / totalClients,
        averageOrderValue,
        customerLifetimeValue: totalRevenue / totalClients,
        churnRate: clients.filter(client => client.churnRisk > 0.7).length / totalClients,
        revenueByRegion: regions.map(region => ({
          region,
          revenue: clients
            .filter(client => client.region === region)
            .reduce((sum, client) => sum + client.totalSpent, 0)
        })),
        clientsBySegment: segments.map(segment => ({
          segment,
          count: clients.filter(client => client.segment === segment).length
        }))
      },
      timeData: this.generateTimeSeriesData(clients),
      segmentAnalysis: this.generateSegmentAnalysis(clients, segments),
      recentClients: clients.sort((a, b) => b.registrationDate - a.registrationDate).slice(0, 10),
      topSpenders: clients.sort((a, b) => b.totalSpent - a.totalSpent).slice(0, 10)
    };
  }
  
  // Gera dados de série temporal para o dashboard
  generateTimeSeriesData(clients) {
    const now = new Date();
    const monthsBack = 12;
    const monthlyData = [];
    
    for (let i = 0; i < monthsBack; i++) {
      const targetMonth = new Date(now);
      targetMonth.setMonth(now.getMonth() - i);
      targetMonth.setDate(1); // Primeiro dia do mês
      
      const yearMonth = `${targetMonth.getFullYear()}-${String(targetMonth.getMonth() + 1).padStart(2, '0')}`;
      
      const monthStart = new Date(targetMonth);
      const monthEnd = new Date(targetMonth.getFullYear(), targetMonth.getMonth() + 1, 0);
      
      // Filtrar compras deste mês
      const monthPurchases = clients.flatMap(client => 
        client.purchases.filter(purchase => 
          purchase.date >= monthStart && purchase.date <= monthEnd
        )
      );
      
      // Novos clientes neste mês
      const newClients = clients.filter(client => 
        client.registrationDate >= monthStart && client.registrationDate <= monthEnd
      ).length;
      
      monthlyData.push({
        month: yearMonth,
        monthLabel: targetMonth.toLocaleDateString('default', { month: 'short', year: 'numeric' }),
        revenue: monthPurchases.reduce((sum, purchase) => sum + purchase.total, 0),
        transactions: monthPurchases.length,
        newClients,
        averageOrderValue: monthPurchases.length === 0 ? 0 : 
          monthPurchases.reduce((sum, purchase) => sum + purchase.total, 0) / monthPurchases.length
      });
    }
    
    // Reverter para ordem cronológica
    return monthlyData.reverse();
  }
  
  // Gera análise por segmento
  generateSegmentAnalysis(clients, segments) {
    return segments.map(segment => {
      const segmentClients = clients.filter(client => client.segment === segment);
      
      let totalRevenue = 0;
      let totalPurchases = 0;
      
      segmentClients.forEach(client => {
        totalRevenue += client.totalSpent;
        totalPurchases += client.totalPurchases;
      });
      
      return {
        segment,
        clientCount: segmentClients.length,
        revenue: totalRevenue,
        averageSpend: segmentClients.length === 0 ? 0 : totalRevenue / segmentClients.length,
        purchaseFrequency: segmentClients.length === 0 ? 0 
          : segmentClients.reduce((sum, client) => sum + client.purchaseFrequency, 0) / segmentClients.length,
        churnRate: segmentClients.length === 0 ? 0
          : segmentClients.filter(client => client.churnRisk > 0.7).length / segmentClients.length,
        satisfaction: segmentClients.length === 0 ? 0
          : segmentClients.reduce((sum, client) => sum + client.satisfaction, 0) / segmentClients.length,
        averageOrderValue: totalPurchases === 0 ? 0 : totalRevenue / totalPurchases
      };
    });
  }
  
  // Configuração dos filtros
  applyFilters() {
    this.showLoadingIndicator();
    
    const dateRangeFilter = document.getElementById('date-range-filter').value;
    const segmentFilter = document.getElementById('segment-filter').value;
    const regionFilter = document.getElementById('region-filter').value;
    
    this.filters = {
      dateRange: dateRangeFilter,
      segment: segmentFilter,
      region: regionFilter
    };
    
    // Aplicar filtros nos dados
    let filtered = [...this.data.clients];
    
    // Filtro de data
    if (dateRangeFilter !== 'all') {
      const daysBack = parseInt(dateRangeFilter, 10);
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - daysBack);
      
      filtered = filtered.filter(client => client.registrationDate >= cutoffDate);
    }
    
    // Filtro de segmento
    if (segmentFilter !== 'all') {
      const segmentName = segmentFilter.charAt(0).toUpperCase() + segmentFilter.slice(1);
      filtered = filtered.filter(client => client.segment === segmentName);
    }
    
    // Filtro de região
    if (regionFilter !== 'all') {
      const regionName = regionFilter.charAt(0).toUpperCase() + regionFilter.slice(1);
      filtered = filtered.filter(client => client.region.toLowerCase() === regionFilter);
    }
    
    // Atualizar dados filtrados
    this.filteredData = {
      ...this.data,
      clients: filtered
    };
    
    // Recalcular métricas com base nos dados filtrados
    this.recalculateMetrics();
    
    // Atualizar visualizações
    this.updateCharts();
    
    this.hideLoadingIndicator();
  }
  
  // Recalcula métricas baseado nos filtros
  recalculateMetrics() {
    const clients = this.filteredData.clients;
    const regions = ['Norte', 'Nordeste', 'Centro-Oeste', 'Sudeste', 'Sul'];
    const segments = ['Premium', 'Standard', 'Básico'];
    
    const totalRevenue = clients.reduce((sum, client) => sum + client.totalSpent, 0);
    const totalClients = clients.length;
    const activeClients = clients.filter(client => client.status === 'Ativo').length;
    const totalPurchases = clients.reduce((sum, client) => sum + client.totalPurchases, 0);
    
    this.filteredData.metrics = {
      totalRevenue,
      totalClients,
      activeClients,
      inactiveRate: totalClients === 0 ? 0 : (totalClients - activeClients) / totalClients,
      averageOrderValue: totalPurchases === 0 ? 0 : totalRevenue / totalPurchases,
      customerLifetimeValue: totalClients === 0 ? 0 : totalRevenue / totalClients,
      churnRate: totalClients === 0 ? 0 
        : clients.filter(client => client.churnRisk > 0.7).length / totalClients,
      revenueByRegion: regions.map(region => ({
        region,
        revenue: clients
          .filter(client => client.region === region)
          .reduce((sum, client) => sum + client.totalSpent, 0)
      })),
      clientsBySegment: segments.map(segment => ({
        segment,
        count: clients.filter(client => client.segment === segment).length
      }))
    };
    
    this.filteredData.timeData = this.generateTimeSeriesData(clients);
    this.filteredData.segmentAnalysis = this.generateSegmentAnalysis(clients, segments);
    this.filteredData.recentClients = clients
      .sort((a, b) => b.registrationDate - a.registrationDate)
      .slice(0, 10);
    this.filteredData.topSpenders = clients
      .sort((a, b) => b.totalSpent - a.totalSpent)
      .slice(0, 10);
  }
  
  // Criação do dashboard principal
  createDashboard() {
    const grid = document.getElementById('dashboard-grid');
    
    // Limpar conteúdo existente
    grid.innerHTML = '';
    
    // Adicionar KPIs
    this.createKPISection(grid);
    
    // Adicionar gráficos principais
    this.createMainCharts(grid);
    
    // Adicionar análise de segmento
    this.createSegmentAnalysis(grid);
    
    // Adicionar gráficos adicionais
    this.createAdditionalCharts(grid);
    
    // Adicionar tabelas
    this.createTables(grid);
  }
  
  // Seção de KPIs
  createKPISection(grid) {
    // Receita Total
    const totalRevenueCard = this.createCard(3, 1);
    totalRevenueCard.classList.add('kpi-card');
    totalRevenueCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Receita Total</h3>
      </div>
      <div class="card-content">
        <div class="kpi-value" id="kpi-total-revenue">
          R$ ${this.formatCurrency(this.filteredData.metrics.totalRevenue)}
        </div>
        <div class="kpi-label">Total de vendas no período</div>
      </div>
    `;
    grid.appendChild(totalRevenueCard);
    
    // Total de Clientes
    const totalClientsCard = this.createCard(3, 1);
    totalClientsCard.classList.add('kpi-card');
    totalClientsCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Total de Clientes</h3>
      </div>
      <div class="card-content">
        <div class="kpi-value" id="kpi-total-clients">
          ${this.formatNumber(this.filteredData.metrics.totalClients)}
        </div>
        <div class="kpi-label">Base de clientes ativos</div>
      </div>
    `;
    grid.appendChild(totalClientsCard);
    
    // Ticket Médio
    const avgOrderCard = this.createCard(3, 1);
    avgOrderCard.classList.add('kpi-card');
    avgOrderCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Ticket Médio</h3>
      </div>
      <div class="card-content">
        <div class="kpi-value" id="kpi-avg-order">
          R$ ${this.formatCurrency(this.filteredData.metrics.averageOrderValue)}
        </div>
        <div class="kpi-label">Valor médio por compra</div>
      </div>
    `;
    grid.appendChild(avgOrderCard);
    
    // Taxa de Churn
    const churnRateCard = this.createCard(3, 1);
    churnRateCard.classList.add('kpi-card');
    churnRateCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Taxa de Churn</h3>
      </div>
      <div class="card-content">
        <div class="kpi-value ${this.filteredData.metrics.churnRate < 0.2 ? 'kpi-positive' : 'kpi-negative'}" id="kpi-churn-rate">
          ${(this.filteredData.metrics.churnRate * 100).toFixed(1)}%
        </div>
        <div class="kpi-label">Clientes em risco de saída</div>
      </div>
    `;
    grid.appendChild(churnRateCard);
  }
  
  // Gráficos principais
  createMainCharts(grid) {
    // Gráfico de Receita Mensal
    const revenueChartCard = this.createCard(6, 2);
    revenueChartCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Evolução da Receita</h3>
      </div>
      <div class="card-content">
        <canvas id="revenue-chart" width="100%" height="250"></canvas>
      </div>
    `;
    grid.appendChild(revenueChartCard);
    
    // Gráfico de Clientes por Segmento
    const segmentChartCard = this.createCard(6, 2);
    segmentChartCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Distribuição por Segmento</h3>
      </div>
      <div class="card-content">
        <canvas id="segment-chart" width="100%" height="250"></canvas>
      </div>
    `;
    grid.appendChild(segmentChartCard);
    
    // Criar os gráficos após adicionar os elementos ao DOM
    setTimeout(() => {
      this.createRevenueChart();
      this.createSegmentChart();
    }, 0);
  }
  
  // Análise de segmento
  createSegmentAnalysis(grid) {
    const segmentAnalysisCard = this.createCard(12, 2);
    segmentAnalysisCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Análise por Segmento</h3>
      </div>
      <div class="card-content">
        <div id="segment-analysis-container" style="display: flex; justify-content: space-around; flex-wrap: wrap;">
          ${this.filteredData.segmentAnalysis.map(segment => `
            <div class="segment-box" style="flex: 1; min-width: 230px; padding: 15px; margin: 10px; background-color: ${this.config.theme === 'dark' ? '#3D4A5C' : '#F7FAFC'}; border-radius: 8px;">
              <h4 style="margin-top: 0; color: ${this.config.colors.primary[0]};">${segment.segment}</h4>
              <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span>Clientes:</span>
                  <strong>${this.formatNumber(segment.clientCount)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span>Receita:</span>
                  <strong>R$ ${this.formatCurrency(segment.revenue)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span>Gasto Médio:</span>
                  <strong>R$ ${this.formatCurrency(segment.averageSpend)}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span>Frequência de Compra:</span>
                  <strong>${segment.purchaseFrequency.toFixed(1)}/mês</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                  <span>Satisfação:</span>
                  <strong>${segment.satisfaction.toFixed(1)}/5 
                    ${this.createStarRating(segment.satisfaction)}
                  </strong>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
    grid.appendChild(segmentAnalysisCard);
  }
  
  // Gráficos adicionais
  createAdditionalCharts(grid) {
    // Gráfico de Receita por Região
    const regionChartCard = this.createCard(6, 2);
    regionChartCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Receita por Região</h3>
      </div>
      <div class="card-content">
        <canvas id="region-chart" width="100%" height="250"></canvas>
      </div>
    `;
    grid.appendChild(regionChartCard);
    
    // Gráfico de Novos Clientes
    const newClientsChartCard = this.createCard(6, 2);
    newClientsChartCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Novos Clientes por Mês</h3>
      </div>
      <div class="card-content">
        <canvas id="new-clients-chart" width="100%" height="250"></canvas>
      </div>
    `;
    grid.appendChild(newClientsChartCard);
    
    // Criar os gráficos após adicionar os elementos ao DOM
    setTimeout(() => {
      this.createRegionChart();
      this.createNewClientsChart();
    }, 0);
  }
  
  // Tabelas de dados
  createTables(grid) {
    // Tabela de Top Clientes
    const topClientsCard = this.createCard(6, 2);
    topClientsCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Top Clientes por Valor</h3>
      </div>
      <div class="card-content">
        <div class="table-responsive">
          <table class="dashboard-table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Segmento</th>
                <th>Valor Total</th>
                <th>Compras</th>
              </tr>
            </thead>
            <tbody>
              ${this.filteredData.topSpenders.slice(0, 5).map(client => `
                <tr>
                  <td>${client.name}</td>
                  <td><span class="badge ${client.segment.toLowerCase()}">${client.segment}</span></td>
                  <td>R$ ${this.formatCurrency(client.totalSpent)}</td>
                  <td>${client.totalPurchases}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
    grid.appendChild(topClientsCard);
    
    // Tabela de Clientes Recentes
    const recentClientsCard = this.createCard(6, 2);
    recentClientsCard.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">Clientes Recentes</h3>
      </div>
      <div class="card-content">
        <div class="table-responsive">
          <table class="dashboard-table">
            <thead>
              <tr>
                <th>Cliente</th>
                <th>Data de Registro</th>
                <th>Região</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${this.filteredData.recentClients.slice(0, 5).map(client => `
                <tr>
                  <td>${client.name}</td>
                  <td>${client.registrationDate.toLocaleDateString()}</td>
                  <td>${client.region}</td>
                  <td><span class="badge ${client.status.toLowerCase()}">${client.status}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
    grid.appendChild(recentClientsCard);
    
    // Adicionar estilos para tabelas
    const tableStyle = document.createElement('style');
    tableStyle.textContent = `
      .table-responsive {
        overflow-x: auto;
        margin-top: 10px;
      }
      
      .dashboard-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
      }
      
      .dashboard-table th {
        padding: 12px 15px;
        text-align: left;
        background-color: ${this.config.theme === 'dark' ? '#3D4A5C' : '#F7FAFC'};
        color: var(--color-text);
        font-weight: 600;
      }
      
      .dashboard-table td {
        padding: 10px 15px;
        border-bottom: 1px solid ${this.config.theme === 'dark' ? '#4A5568' : '#E2E8F0'};
      }
      
      .dashboard-table tr:last-child td {
        border-bottom: none;
      }
      
      .dashboard-table tr:hover td {
        background-color: ${this.config.theme === 'dark' ? '#4A5568' : '#EDF2F7'};
      }
      
      .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
      }
      
      .badge.premium {
        background-color: #FEF3C7;
        color: #92400E;
      }
      
      .badge.standard {
        background-color: #DBEAFE;
        color: #1E40AF;
      }
      
      .badge.básico {
        background-color: #E0E7FF;
        color: #3730A3;
      }
      
      .badge.ativo {
        background-color: #D1FAE5;
        color: #065F46;
      }
      
      .badge.inativo {
        background-color: #FEE2E2;
        color: #991B1B;
      }
      
      .badge.pendente {
        background-color: #FEF3C7;
        color: #92400E;
      }
    `;
    document.head.appendChild(tableStyle);
  }
  
  // Criação de gráfico de receita mensal
  createRevenueChart() {
    const ctx = document.getElementById('revenue-chart').getContext('2d');
    
    const monthLabels = this.filteredData.timeData.map(item => item.monthLabel);
    const revenueData = this.filteredData.timeData.map(item => item.revenue);
    
    if (this.charts.revenueChart) {
      this.charts.revenueChart.destroy();
    }
    
    this.charts.revenueChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: monthLabels,
        datasets: [{
          label: 'Receita Mensal',
          data: revenueData,
          backgroundColor: this.config.colors.primary[0] + '33', // 20% opacity
          borderColor: this.config.colors.primary[0],
          borderWidth: 2,
          tension: 0.3,
          fill: 'start'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                return `Receita: R$ ${new Intl.NumberFormat('pt-BR').format(context.parsed.y.toFixed(2))}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return `R$ ${value.toLocaleString('pt-BR', {maximumFractionDigits: 0})}`;
              }
            }
          }
        }
      }
    });
  }
  
  // Criação de gráfico de clientes por segmento
  createSegmentChart() {
    const ctx = document.getElementById('segment-chart').getContext('2d');
    
    const segmentData = this.filteredData.metrics.clientsBySegment;
    const labels = segmentData.map(item => item.segment);
    const counts = segmentData.map(item => item.count);
    
    if (this.charts.segmentChart) {
      this.charts.segmentChart.destroy();
    }
    
    this.charts.segmentChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: [
            this.config.colors.primary[0],
            this.config.colors.primary[2],
            this.config.colors.primary[4]
          ],
          borderColor: this.config.theme === 'dark' ? '#2D3748' : '#FFFFFF',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.parsed || 0;
                const total = context.dataset.data.reduce((acc, data) => acc + data, 0);
                const percentage = ((value * 100) / total).toFixed(1);
                return `${label}: ${value} clientes (${percentage}%)`;
              }
            }
          }
        }
      }
    });
  }
  
  // Criação de gráfico de receita por região
  createRegionChart() {
    const ctx = document.getElementById('region-chart').getContext('2d');
    
    const regionData = this.filteredData.metrics.revenueByRegion;
    const labels = regionData.map(item => item.region);
    const values = regionData.map(item => item.revenue);
    
    if (this.charts.regionChart) {
      this.charts.regionChart.destroy();
    }
    
    this.charts.regionChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Receita por Região',
          data: values,
          backgroundColor: this.config.colors.secondary,
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return `Receita: R$ ${new Intl.NumberFormat('pt-BR').format(context.parsed.y.toFixed(2))}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return `R$ ${value.toLocaleString('pt-BR', {maximumFractionDigits: 0})}`;
              }
            }
          }
        }
      }
    });
  }
  
  // Criação de gráfico de novos clientes
  createNewClientsChart() {
    const ctx = document.getElementById('new-clients-chart').getContext('2d');
    
    const monthLabels = this.filteredData.timeData.map(item => item.monthLabel);
    const newClientsData = this.filteredData.timeData.map(item => item.newClients);
    
    if (this.charts.newClientsChart) {
      this.charts.newClientsChart.destroy();
    }
    
    this.charts.newClientsChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: monthLabels,
        datasets: [{
          label: 'Novos Clientes',
          data: newClientsData,
          backgroundColor: this.config.colors.primary[2],
          borderRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            }
          },
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        }
      }
    });
  }
  
  // Atualiza todos os gráficos com dados filtrados
  updateCharts() {
    // Atualizar KPIs
    document.getElementById('kpi-total-revenue').textContent = 
      `R$ ${this.formatCurrency(this.filteredData.metrics.totalRevenue)}`;
      
    document.getElementById('kpi-total-clients').textContent = 
      this.formatNumber(this.filteredData.metrics.totalClients);
      
    document.getElementById('kpi-avg-order').textContent = 
      `R$ ${this.formatCurrency(this.filteredData.metrics.averageOrderValue)}`;
      
    const churnElement = document.getElementById('kpi-churn-rate');
    churnElement.textContent = `${(this.filteredData.metrics.churnRate * 100).toFixed(1)}%`;
    churnElement.className = `kpi-value ${this.filteredData.metrics.churnRate < 0.2 ? 'kpi-positive' : 'kpi-negative'}`;
    
    // Atualizar gráficos
    this.createRevenueChart();
    this.createSegmentChart();
    this.createRegionChart();
    this.createNewClientsChart();
    
    // Atualizar análise de segmento
    const segmentAnalysisContainer = document.getElementById('segment-analysis-container');
    if (segmentAnalysisContainer) {
      segmentAnalysisContainer.innerHTML = this.filteredData.segmentAnalysis.map(segment => `
        <div class="segment-box" style="flex: 1; min-width: 230px; padding: 15px; margin: 10px; background-color: ${this.config.theme === 'dark' ? '#3D4A5C' : '#F7FAFC'}; border-radius: 8px;">
          <h4 style="margin-top: 0; color: ${this.config.colors.primary[0]};">${segment.segment}</h4>
          <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span>Clientes:</span>
              <strong>${this.formatNumber(segment.clientCount)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span>Receita:</span>
              <strong>R$ ${this.formatCurrency(segment.revenue)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span>Gasto Médio:</span>
              <strong>R$ ${this.formatCurrency(segment.averageSpend)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span>Frequência de Compra:</span>
              <strong>${segment.purchaseFrequency.toFixed(1)}/mês</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span>Satisfação:</span>
              <strong>${segment.satisfaction.toFixed(1)}/5 
                ${this.createStarRating(segment.satisfaction)}
              </strong>
            </div>
          </div>
        </div>
      `).join('');
    }
    
    // Atualizar tabelas
    const topClientsTable = document.querySelector('.dashboard-table:nth-of-type(1) tbody');
    if (topClientsTable) {
      topClientsTable.innerHTML = this.filteredData.topSpenders.slice(0, 5).map(client => `
        <tr>
          <td>${client.name}</td>
          <td><span class="badge ${client.segment.toLowerCase()}">${client.segment}</span></td>
          <td>R$ ${this.formatCurrency(client.totalSpent)}</td>
          <td>${client.totalPurchases}</td>
        </tr>
      `).join('');
    }
    
    const recentClientsTable = document.querySelector('.dashboard-table:nth-of-type(2) tbody');
    if (recentClientsTable) {
      recentClientsTable.innerHTML = this.filteredData.recentClients.slice(0, 5).map(client => `
        <tr>
          <td>${client.name}</td>
          <td>${client.registrationDate.toLocaleDateString()}</td>
          <td>${client.region}</td>
          <td><span class="badge ${client.status.toLowerCase()}">${client.status}</span></td>
        </tr>
      `).join('');
    }
  }
  
  // Configurar listeners de eventos
  setupEventListeners() {
    // Listeners para filtros
    const dateRangeFilter = document.getElementById('date-range-filter');
    const segmentFilter = document.getElementById('segment-filter');
    const regionFilter = document.getElementById('region-filter');
    
    dateRangeFilter.addEventListener('change', () => this.applyFilters());
    segmentFilter.addEventListener('change', () => this.applyFilters());
    regionFilter.addEventListener('change', () => this.applyFilters());
    
    // Listener para alternância de tema
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => this.toggleTheme());
    
    // Listener para exportação de PDF
    const exportPdfButton = document.getElementById('export-pdf');
    exportPdfButton.addEventListener('click', () => this.exportToPdf());
  }
  
  // Alternância de tema claro/escuro
  toggleTheme() {
    this.config.theme = this.config.theme === 'light' ? 'dark' : 'light';
    
    if (this.config.theme === 'dark') {
      this.config.colors.background = "#1A202C";
      this.config.colors.cardBackground = "#2D3748";
      this.config.colors.text = "#F7FAFC";
      this.config.colors.lightText = "#A0AEC0";
      document.body.classList.add('dark-theme');
    } else {
      this.config.colors.background = "#F9FAFB";
      this.config.colors.cardBackground = "#FFFFFF";
      this.config.colors.text = "#1E293B";
      this.config.colors.lightText = "#64748B";
      document.body.classList.remove('dark-theme');
    }
    
    // Atualizar variáveis CSS
    document.documentElement.style.setProperty('--color-background', this.config.colors.background);
    document.documentElement.style.setProperty('--color-card-bg', this.config.colors.cardBackground);
    document.documentElement.style.setProperty('--color-text', this.config.colors.text);
    document.documentElement.style.setProperty('--color-light-text', this.config.colors.lightText);
    
    // Atualizar gráficos
    this.updateCharts();
  }
  
  // Exportação para PDF
  exportToPdf() {
    // Aqui seria implementada a exportação para PDF
    // Usando uma biblioteca como jsPDF ou html2pdf
    alert('Funcionalidade de exportação para PDF não implementada nesta versão de demonstração.');
  }
  
  // Atualização automática
  startAutoRefresh() {
    if (this.config.refreshInterval > 0) {
      setInterval(() => {
        this.loadData().then(() => {
          this.applyFilters();
        });
      }, this.config.refreshInterval);
    }
  }
  
  // Utilitários
  
  // Criar um card para o dashboard grid
  createCard(width, height) {
    const card = document.createElement('div');
    card.className = 'dashboard-card';
    card.style.gridColumn = `span ${width}`;
    card.style.gridRow = `span ${height}`;
    return card;
  }
  
  // Formatação de moeda
  formatCurrency(value) {
    return value.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }
  
  // Formatação de números
  formatNumber(value) {
    return value.toLocaleString('pt-BR');
  }
  
  // Criar classificação por estrelas
  createStarRating(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    let starsHtml = '';
    
    // Estrelas cheias
    for (let i = 0; i < fullStars; i++) {
      starsHtml += '<span style="color: gold;">★</span>';
    }
    
    // Meia estrela
    if (halfStar) {
      starsHtml += '<span style="color: gold;">★</span>';
    }
    
    // Estrelas vazias
    for (let i = 0; i < emptyStars; i++) {
      starsHtml += '<span style="color: #CBD5E0;">★</span>';
    }
    
    return starsHtml;
  }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  // Carregar bibliotecas necessárias
  Promise.all([
    loadScript('https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js'),
    loadScript('https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js')
  ]).then(() => {
    // Inicializar o dashboard
    const dashboard = new ClientDashboard('dashboard-root');
  }).catch(error => {
    console.error('Erro ao carregar as bibliotecas necessárias:', error);
  });
});

// Função para carregar scripts externos
function loadScript(src) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = src;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}