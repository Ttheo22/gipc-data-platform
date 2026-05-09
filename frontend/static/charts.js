const GIPC_GREEN   = '#006633';
const GIPC_GOLD    = '#FCD116';
const API          = '';
const DEFAULT_FROM = 1995;
const DEFAULT_TO   = 2024;

// ── Chart Instance Registry ────────────────────────────────
const chartInstances = {};

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

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

function showError(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const div = document.createElement('div');
    div.style.cssText = 'text-align:center;padding:2rem;color:#999;font-size:0.9rem;';
    div.textContent = message;
    canvas.replaceWith(div);
}

function makeLineChart(canvasId, labels, datasets) {
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
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
    destroyChart(canvasId);
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    chartInstances[canvasId] = new Chart(ctx, {
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

// ── Year Filter ───────────────────────────────────────────
function getYearRange() {
    const from = parseInt(document.getElementById('year-from')?.value) || DEFAULT_FROM;
    const to   = parseInt(document.getElementById('year-to')?.value)   || DEFAULT_TO;
    return { from, to };
}

function populateYearDropdowns() {
    const fromSelect = document.getElementById('year-from');
    const toSelect   = document.getElementById('year-to');
    if (!fromSelect || !toSelect) return;

    for (let y = 1980; y <= 2031; y++) {
        const o1 = document.createElement('option');
        o1.value = y; o1.textContent = y;
        if (y === DEFAULT_FROM) o1.selected = true;
        fromSelect.appendChild(o1);

        const o2 = document.createElement('option');
        o2.value = y; o2.textContent = y;
        if (y === DEFAULT_TO) o2.selected = true;
        toSelect.appendChild(o2);
    }
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
    set('val-inflation', 'inflation_cpi',     1);
    set('val-fx',        'exchange_rate_usd', 2);
    set('val-growth',    'gdp_growth_rate',   1);
}

// ── GDP Chart ─────────────────────────────────────────────
async function loadGDPChart() {
    const { from, to } = getYearRange();
    const data = await fetchJSON(
        `${API}/api/data?indicator=gdp_current_usd&source=world_bank&year_from=${from}&year_to=${to}`
    );
    if (!data || !data.length) { showError('chart-gdp', 'No GDP data available'); return; }

    makeLineChart('chart-gdp', data.map(d => d.year), [{
        label: 'GDP (USD Billions)',
        data: data.map(d => parseFloat(d.value)),
        borderColor: GIPC_GREEN,
        backgroundColor: 'rgba(0,102,51,0.08)',
        tension: 0.3,
        fill: true,
        pointRadius: 3,
    }]);
}

// ── FDI Chart ─────────────────────────────────────────────
async function loadFDIChart() {
    const { from, to } = getYearRange();
    const data = await fetchJSON(
        `${API}/api/data?indicator=fdi_net_inflows_usd&source=world_bank&year_from=${from}&year_to=${to}`
    );
    if (!data || !data.length) { showError('chart-fdi', 'No FDI data available'); return; }

    makeBarChart('chart-fdi', data.map(d => d.year), data.map(d => parseFloat(d.value)), 'FDI Net Inflows (USD Billions)');
}

// ── Inflation vs Growth Chart ──────────────────────────────
async function loadInflationGrowthChart() {
    const { from, to } = getYearRange();
    const [inflation, growth] = await Promise.all([
        fetchJSON(`${API}/api/data?indicator=inflation_cpi&source=world_bank&year_from=${from}&year_to=${to}`),
        fetchJSON(`${API}/api/data?indicator=gdp_growth_rate&source=world_bank&year_from=${from}&year_to=${to}`)
    ]);

    if (!inflation || !inflation.length) {
        showError('chart-inflation-growth', 'No inflation/growth data available');
        return;
    }

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

    makeLineChart('chart-inflation-growth', inflation.map(d => d.year), datasets);
}

// ── Exchange Rate Chart ────────────────────────────────────
async function loadFXChart() {
    const { from, to } = getYearRange();
    const data = await fetchJSON(
        `${API}/api/data?indicator=exchange_rate_usd&source=world_bank&year_from=${from}&year_to=${to}`
    );
    if (!data || !data.length) { showError('chart-fx', 'No exchange rate data available'); return; }

    makeLineChart('chart-fx', data.map(d => d.year), [{
        label: 'GHS per USD',
        data: data.map(d => parseFloat(d.value)),
        borderColor: GIPC_GOLD,
        backgroundColor: 'rgba(252,209,22,0.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 3,
    }]);
}

// ── Domestic Table ─────────────────────────────────────────
async function loadDomesticTable() {
    const data  = await fetchJSON(`${API}/api/domestic`);
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
    const el   = document.getElementById('last-updated');
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

// ── Reload Charts Only (for filter) ───────────────────────
async function reloadCharts() {
    await Promise.allSettled([
        loadGDPChart(),
        loadFDIChart(),
        loadInflationGrowthChart(),
        loadFXChart(),
    ]);
}

// ── Init ──────────────────────────────────────────────────
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

// ── Morning Refresh Scheduler ─────────────────────────────
function scheduleMorningRefresh() {
    const now    = new Date();
    const target = new Date();
    target.setHours(8, 0, 0, 0);
    if (now >= target) target.setDate(target.getDate() + 1);
    const msUntil8am = target - now;
    console.log(`Next data refresh in ${Math.round(msUntil8am / 60000)} minutes`);
    setTimeout(async () => {
        console.log('Morning refresh at', new Date().toLocaleTimeString());
        await init();
        scheduleMorningRefresh();
    }, msUntil8am);
}

// ── Manual Refresh Button ─────────────────────────────────
function addRefreshButton() {
    const header = document.querySelector('.header-right');
    if (!header) return;
    const btn = document.createElement('button');
    btn.textContent   = 'Refresh Data';
    btn.style.cssText = `
        background: transparent;
        border: 1px solid #FCD116;
        color: #FCD116;
        padding: 6px 14px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
        margin-left: 16px;
        transition: all 0.2s;
    `;
    btn.addEventListener('mouseenter', () => { btn.style.background = '#FCD116'; btn.style.color = '#004d26'; });
    btn.addEventListener('mouseleave', () => { btn.style.background = 'transparent'; btn.style.color = '#FCD116'; });
    btn.addEventListener('click', async () => {
        btn.textContent = 'Refreshing...';
        btn.disabled    = true;
        await init();
        btn.textContent = 'Refresh Data';
        btn.disabled    = false;
    });
    header.appendChild(btn);
}

// ── Boot ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    populateYearDropdowns();

    document.getElementById('apply-filter')?.addEventListener('click', () => {
        const from = parseInt(document.getElementById('year-from').value);
        const to   = parseInt(document.getElementById('year-to').value);
        if (from > to) { alert('Start year cannot be greater than end year.'); return; }
        reloadCharts();
    });

    document.getElementById('reset-filter')?.addEventListener('click', () => {
        document.getElementById('year-from').value = DEFAULT_FROM;
        document.getElementById('year-to').value   = DEFAULT_TO;
        reloadCharts();
    });

    init();
    scheduleMorningRefresh();
    addRefreshButton();
});