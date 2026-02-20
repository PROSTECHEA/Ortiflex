// Mock Data Storage
const STORAGE_KEY = 'oscm_sim_db';

const defaultData = {
    materials: [
        { id: 1, name: 'Tinta Flexográfica Cyan', quantity: 15.5, unit: 'Litros', min_stock: 5, supplier: 'Chimicolor' },
        { id: 2, name: 'Sustrato Autoadhesivo Mate', quantity: 120, unit: 'Metros', min_stock: 50, supplier: 'Sustratos Vzla' },
        { id: 3, name: 'Barniz UV Brillante', quantity: 8, unit: 'Litros', min_stock: 10, supplier: 'Quimicos Flexo' }
    ],
    projects: [
        { id: 1, name: 'Etiquetas Agua Minalba', status: 'En ejecución', client: 'PepsiCo' },
        { id: 2, name: 'Empaque Harina PAN', status: 'Planificado', client: 'Empresas Polar' }
    ],
    currentUser: { username: 'Admin_Demo', role: 'Admin' }
};

// Initialize DB
function getDB() {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : defaultData;
}

function saveDB(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

// Router Simple
function navigate(view) {
    const content = document.getElementById('view-content');
    const links = document.querySelectorAll('.sidebar a');
    links.forEach(l => l.classList.remove('active'));
    
    document.querySelector(`[onclick="navigate('${view}')"]`)?.classList.add('active');

    if (view === 'dashboard') renderDashboard(content);
    if (view === 'inventory') renderInventory(content);
    if (view === 'projects') renderProjects(content);
}

// Renderers
function renderDashboard(container) {
    const db = getDB();
    const lowStock = db.materials.filter(m => m.quantity <= m.min_stock).length;
    
    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold">Dashboard de Simulación</h2>
            <span class="badge bg-info text-dark">Modo Previsualización</span>
        </div>
        <div class="row g-3">
            <div class="col-md-4">
                <div class="card stat-card p-4 text-center">
                    <div class="display-6 font-bold">${db.materials.length}</div>
                    <div class="small opacity-75">Materiales en Sistema</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-white p-4 text-center border-start border-4 border-danger">
                    <div class="display-6 fw-bold text-danger">${lowStock}</div>
                    <div class="small text-muted">Alertas de Stock Bajo</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-white p-4 text-center border-start border-4 border-success">
                    <div class="display-6 fw-bold text-success">${db.projects.length}</div>
                    <div class="small text-muted">Proyectos Activos</div>
                </div>
            </div>
        </div>
        <div class="mt-5">
            <div class="card p-4">
                <h5 class="mb-3">Bienvenido a la Previsualización de Ortiflex OSCM</h5>
                <p>Esta es una versión estática funcional que corre directamente en tu navegador. Puedes interactuar con el menú de la izquierda para ver cómo luce la aplicación final.</p>
                <div class="alert alert-warning small">
                    <i class="bi bi-info-circle me-2"></i> Los cambios realizados aquí se guardan localmente en tu navegador.
                </div>
            </div>
        </div>
    `;
}

function renderInventory(container) {
    const db = getDB();
    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold">Inventario Real-Time</h2>
            <button class="btn btn-primary" onclick="addMaterialSim()">+ Agregar Item</button>
        </div>
        <div class="card shadow-sm border-0">
            <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Material</th>
                            <th>Stock</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${db.materials.map(m => `
                            <tr>
                                <td>${m.name}<br><small class="text-muted">${m.supplier}</small></td>
                                <td><strong>${m.quantity}</strong> ${m.unit}</td>
                                <td>${m.quantity <= m.min_stock ? '<span class="badge bg-danger">Bajo Stock</span>' : '<span class="badge bg-success">Óptimo</span>'}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary"><i class="bi bi-pencil"></i></button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteSim(${m.id})"><i class="bi bi-trash"></i></button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function renderProjects(container) {
    const db = getDB();
    container.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold">Proyectos y Producción</h2>
        </div>
        <div class="row g-4">
            ${db.projects.map(p => `
                <div class="col-md-6">
                    <div class="card p-3 h-100 border-start border-4 ${p.status === 'En ejecución' ? 'border-primary' : 'border-warning'}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h5 class="mb-1">${p.name}</h5>
                                <div class="text-muted small">${p.client}</div>
                            </div>
                            <span class="badge ${p.status === 'En ejecución' ? 'bg-primary' : 'bg-warning text-dark'}">${p.status}</span>
                        </div>
                        <div class="mt-3">
                            <div class="progress" style="height: 10px;">
                                <div class="progress-bar" style="width: ${p.status === 'En ejecución' ? '45%' : '0%'}"></div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function deleteSim(id) {
    if(confirm('¿Desea eliminar este material de la simulación?')) {
        let db = getDB();
        db.materials = db.materials.filter(m => m.id !== id);
        saveDB(db);
        renderInventory(document.getElementById('view-content'));
    }
}

function addMaterialSim() {
    const name = prompt('Nombre del nuevo material (Simulado):');
    if(name) {
        let db = getDB();
        db.materials.push({
            id: Date.now(),
            name: name,
            quantity: 10,
            unit: 'Unid',
            min_stock: 5,
            supplier: 'Nuevo Proveedor'
        });
        saveDB(db);
        renderInventory(document.getElementById('view-content'));
    }
}

// Start
document.addEventListener('DOMContentLoaded', () => {
    navigate('dashboard');
});
