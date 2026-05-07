const GIPC_GREEN = '#006633';
const GIPC_GOLD  = '#FCD116';
const API        = '';

// ── Helpers ───────────────────────────────────────────────
async function fetchJSON(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) {
            console.warn(`API warning [${res.status}]: ${url}`);
            return null;
        }
        return res.json();
    } catch (err) {
        console.warn(`Fetch failed: ${url}`, err);
        return null;
    }
}

function makeLineChart(canvasId, labels, datasets) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { grid: { color: '#e8f0e8' } },
                y: { grid: { color: '#e8f0e8' } }
            }
        }
    });
}

function makeBarChart(canvasId, labels, data, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label,
                data,
                backgroundColor: GIPC_GREEN,
                borderColor: GIPC_GREEN,
                borderWidth: 1,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: '#e8f0e8' } },
                y: { grid: { color: '#e8f0e8' } }
            }
        }
    });
}

function showError(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const parent = canvas.parentElement;
    const div = document.createElement('div');
    div.style.cssText = 'text-align:center;padding:2rem;color:#999;font-size:0.9rem;';
    div.textContent = message;
    canvas.replaceWith(div);
}

// ── KPI Cards ─────────────────────────────────────────────
async function loadKPIs() {
    const data = await fetchJSON(`${API}/api/kpis`);
    if (!data) return;

    const map = {};
    data.forEach(d => { map[d.indicator_name] = d; });

    const set = (id, key, decimals = 2) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (map[key] && map[key].value != null) {
            el.textContent = parseFloat(map[key].value).toFixed(decimals);
        } else {
            el.textContent = 'N/A';
            console.warn(`KPI missing: ${key}`);
        }
    };

    set('val-gdp',       'gdp_current_usd');
    set('val-fdi',       'fdi_net_inflows_usd');
    set('val-inflation', 'inflation_cpi',    1);
    set('val-fx',        'exchange_rate_usd', 2);
    set('val-growth',    'gdp_growth_rate',  1);
}

// ── GDP Chart ─────────────────────────────────────────────
async function loadGDPChart() {
    const data = await fetchJSON(
        `${API}/api/data?indicator=gdp_current_usd&source=world_bank&year_from=1995&year_to=2024`
    );
    if (!data || !data.length) { showError('chart-gdp', 'No GDP data available'); return; }

    const labels = data.map(d => d.year);
    const values = data.map(d => parseFloat(d.value));

    makeLineChart('chart-gdp', labels, [{
        label: 'GDP (USD Billions)',
        data: values,
        borderColor: GIPC_GREEN,
        backgroundColor: 'rgba(0,102,51,0.08)',
        tension: 0.3,
        fill: true,
        pointRadius: 3,
    }]);
}

// ── FDI Chart ─────────────────────────────────────────────
async function loadFDIChart() {
    const data = await fetchJSON(
        `${API}/api/data?indicator=fdi_net_inflows_usd&source=world_bank&year_from=2000&year_to=2024`
    );
    if (!data || !data.length) { showError('chart-fdi', 'No FDI data available'); return; }

    const labels = data.map(d => d.year);
    const values = data.map(d => parseFloat(d.value));

    makeBarChart('chart-fdi', labels, values, 'FDI Net Inflows (USD Billions)');
}

// ── Inflation vs Growth Chart ──────────────────────────────
async function loadInflationGrowthChart() {
    const [inflation, growth] = await Promise.all([
        fetchJSON(`${API}/api/data?indicator=inflation_cpi&source=world_bank&year_from=1995&year_to=2024`),
        fetchJSON(`${API}/api/data?indicator=gdp_growth_rate&source=world_bank&year_from=1995&year_to=2024`)
    ]);

    if (!inflation || !inflation.length) {
        showError('chart-inflation-growth', 'No inflation/growth data available');
        return;
    }

    const labels = inflation.map(d => d.year);
    const datasets = [{
        label: 'Inflation CPI (%)',
        data: inflation.map(d => parseFloat(d.value)),
        borderColor: '#cc0000',
        backgroundColor: 'rgba(204,0,0,0.05)',
        tension: 0.3,
        fill: false,
        pointRadius: 2,
    }];

    if (growth && growth.length) {
        datasets.push({
            label: 'GDP Growth Rate (%)',
            data: growth.map(d => parseFloat(d.value)),
            borderColor: GIPC_GREEN,
            backgroundColor: 'rgba(0,102,51,0.05)',
            tension: 0.3,
            fill: false,
            pointRadius: 2,
        });
    }

    makeLineChart('chart-inflation-growth', labels, datasets);
}

// ── Exchange Rate Chart ────────────────────────────────────
async function loadFXChart() {
    const data = await fetchJSON(
        `${API}/api/data?indicator=exchange_rate_usd&source=world_bank&year_from=2000&year_to=2024`
    );
    if (!data || !data.length) { showError('chart-fx', 'No exchange rate data available'); return; }

    const labels = data.map(d => d.year);
    const values = data.map(d => parseFloat(d.value));

    makeLineChart('chart-fx', labels, [{
        label: 'GHS per USD',
        data: values,
        borderColor: GIPC_GOLD,
        backgroundColor: 'rgba(252,209,22,0.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 3,
    }]);
}

// ── Domestic Table ─────────────────────────────────────────
async function loadDomesticTable() {
    const data = await fetchJSON(`${API}/api/domestic`);
    const tbody = document.getElementById('domestic-tbody');
    if (!tbody) return;

    if (!data || !data.length) {
        tbody.innerHTML = '<tr><td colspan="5">No domestic data available</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${row.indicator_name.replace(/_/g, ' ')}</td>
            <td><span class="source-badge source-${row.source.toLowerCase()}">${row.source}</span></td>
            <td>${row.period || row.year}</td>
            <td><strong>${parseFloat(row.value).toFixed(2)}</strong></td>
            <td>${row.unit}</td>
        </tr>
    `).join('');
}

// ── Last Updated ──────────────────────────────────────────
async function loadLastUpdated() {
    const data = await fetchJSON(`${API}/api/last-updated`);
    const el = document.getElementById('last-updated');
    if (!el) return;
    if (data && data.last_updated) {
        const date = new Date(data.last_updated).toLocaleDateString('en-GB', {
            day: 'numeric', month: 'long', year: 'numeric'
        });
        el.textContent = `Last updated: ${date}`;
    } else {
        el.textContent = '';
    }
}

// ── Init — each section loads independently ───────────────
async function init() {
    await Promise.allSettled([
        loadKPIs(),
        loadGDPChart(),
        loadFDIChart(),
        loadInflationGrowthChart(),
        loadFXChart(),
        loadDomesticTable(),
        loadLastUpdated(),
    ]);
}

document.addEventListener('DOMContentLoaded', init);