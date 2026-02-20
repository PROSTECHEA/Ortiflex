/**
 * Ortiflex OSCM - Pure SPA System
 * Complete serverless rewrite for 100% GitHub Pages compatibility.
 */

const app = {
    // --- STATE & STORAGE ---
    STORAGE_KEY: 'oscm_database_v3',
    db: {
        materials: [],
        projects: [],
        users: [],
        activity: [],
        config: { admin_password_hash: 'admin123' }
    },
    currentUser: null,

    init() {
        this.loadDB();
        this.bindEvents();
        this.checkSession();
    },

    loadDB() {
        const data = localStorage.getItem(this.STORAGE_KEY);
        if (data) {
            this.db = JSON.parse(data);
        } else {
            this.seedDB();
        }
    },

    saveDB() {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.db));
    },

    seedDB() {
        this.db.materials = [
            { id: 1, name: 'Tinta Flexográfica Cyan', quantity: 15.5, unit: 'Litros', min_stock: 5, supplier: 'Chimicolor', is_deleted: false },
            { id: 2, name: 'Sustrato Autoadhesivo Mate', quantity: 120, unit: 'Metros', min_stock: 50, supplier: 'Sustratos Vzla', is_deleted: false },
            { id: 3, name: 'Barniz UV Brillante', quantity: 8, unit: 'Litros', min_stock: 10, supplier: 'Quimicos Flexo', is_deleted: false }
        ];
        this.db.projects = [
            { id: 1, name: 'Etiquetas Agua Minalba', status: 'En ejecución', client: 'PepsiCo', start_date: '2026-02-15', materials: [], logs: [{ action: 'Creación', user: 'admin', date: '2026-02-15' }] },
            { id: 2, name: 'Empaque Harina PAN', status: 'Planificado', client: 'Empresas Polar', start_date: '2026-02-20', materials: [], logs: [] }
        ];
        this.db.users = [
            { username: 'admin', role: 'Admin', permissions: { inventory: true, projects: true, reports: true, users: true } },
            { username: 'operador', role: 'Operativo', permissions: { inventory: true, projects: true, reports: false, users: false } }
        ];
        this.saveDB();
    },

    // --- AUTH ---
    login(username, password) {
        const user = this.db.users.find(u => u.username === username);
        if (user && (password === 'admin123' || password === 'op123')) {
            this.currentUser = user;
            this.logActivity('Login');
            this.showMainView();
            return true;
        }
        alert('Credenciales inválidas. Use admin/admin123 o operador/op123');
        return false;
    },

    logout() {
        this.logActivity('Logout');
        this.currentUser = null;
        sessionStorage.removeItem('oscm_active_user');
        document.getElementById('main-view').style.display = 'none';
        document.getElementById('login-view').style.display = 'block';
    },

    checkSession() {
        const saved = sessionStorage.getItem('oscm_active_user');
        if (saved) {
            this.currentUser = JSON.parse(saved);
            this.showMainView();
        }
    },

    showMainView() {
        sessionStorage.setItem('oscm_active_user', JSON.stringify(this.currentUser));
        document.getElementById('login-view').style.display = 'none';
        document.getElementById('main-view').style.display = 'block';
        document.getElementById('sidebar-username').textContent = this.currentUser.username;
        document.getElementById('sidebar-role').textContent = this.currentUser.role.toUpperCase();
        document.getElementById('user-initial').textContent = this.currentUser.username[0].toUpperCase();
        document.getElementById('nav-users').style.display = this.currentUser.permissions.users ? 'block' : 'none';
        this.navigate('dashboard');
    },

    logActivity(action) {
        this.db.activity.push({
            user: this.currentUser ? this.currentUser.username : 'Sistema',
            action: action,
            timestamp: new Date().toLocaleString()
        });
        this.saveDB();
    },

    // --- NAVIGATION ---
    navigate(view) {
        const container = document.getElementById('view-container');
        document.querySelectorAll('#nav-links a').forEach(a => a.classList.remove('active'));
        document.querySelector(`[data-nav="${view}"]`)?.classList.add('active');
        document.getElementById('current-breadcrumb').textContent = view.charAt(0).toUpperCase() + view.slice(1);

        switch (view) {
            case 'dashboard': this.renderDashboard(container); break;
            case 'inventory': this.renderInventory(container); break;
            case 'projects': this.renderProjects(container); break;
            case 'trash': this.renderTrash(container); break;
            case 'reports': this.renderReports(container); break;
            case 'users': this.renderUsers(container); break;
        }
        if (window.innerWidth < 992) document.getElementById('sidebar').classList.remove('show');
    },

    // --- RENDERERS ---
    renderDashboard(container) {
        const activeMats = this.db.materials.filter(m => !m.is_deleted);
        const lowStock = activeMats.filter(m => m.quantity <= m.min_stock).length;
        const activeProjects = this.db.projects.filter(p => p.status === 'En ejecución').length;

        container.innerHTML = `
            <div class="row g-4 mb-4">
                ${this.statCard('Materiales', activeMats.length, 'box-seam', 'primary')}
                ${this.statCard('Alertas Stock', lowStock, 'exclamation-triangle', 'danger', lowStock > 0 ? 'low-stock' : '')}
                ${this.statCard('Proyectos Hoy', activeProjects, 'kanban', 'success')}
            </div>
            <div class="card p-4 border-0 shadow-sm">
                <h5 class="fw-bold mb-3">Accesos Directos</h5>
                <div class="d-flex gap-2">
                    <button class="btn btn-outline-primary" onclick="app.navigate('inventory')">Inventario</button>
                    <button class="btn btn-outline-success" onclick="app.navigate('projects')">Nuevo Proyecto</button>
                    <button class="btn btn-outline-dark" onclick="app.exportBackup()">Backup JSON</button>
                </div>
            </div>
        `;
    },

    statCard(title, val, icon, color, extraClass = '') {
        return `
            <div class="col-md-4">
                <div class="card p-3 border-0 bg-white">
                    <div class="d-flex align-items-center">
                        <div class="bg-${color} bg-opacity-10 p-3 rounded-circle me-3">
                            <i class="bi bi-${icon} text-${color} fs-4"></i>
                        </div>
                        <div>
                            <h3 class="fw-bold mb-0 ${extraClass}">${val}</h3>
                            <div class="text-muted small">${title}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    renderInventory(container) {
        const mats = this.db.materials.filter(m => !m.is_deleted);
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="fw-bold m-0">Inventario Global</h2>
                <button class="btn btn-primary" onclick="app.showMaterialModal()">+ Nuevo Item</button>
            </div>
            <div class="card border-0 shadow-sm overflow-hidden">
                <table class="table table-hover align-middle mb-0">
                    <thead class="bg-light"><tr><th>Nombre</th><th>Stock</th><th>Min.</th><th>Acciones</th></tr></thead>
                    <tbody>
                        ${mats.map(m => `
                            <tr>
                                <td class="fw-bold">${m.name}</td>
                                <td class="${m.quantity <= m.min_stock ? 'text-danger fw-bold' : ''}">${m.quantity} ${m.unit}</td>
                                <td class="text-muted small">${m.min_stock} ${m.unit}</td>
                                <td>
                                    <button class="btn btn-sm btn-light" onclick="app.showMaterialModal(${m.id})"><i class="bi bi-pencil"></i></button>
                                    <button class="btn btn-sm btn-light text-danger" onclick="app.deleteMaterial(${m.id})"><i class="bi bi-trash"></i></button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="4" class="text-center p-4">Vacío</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    },

    renderProjects(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="fw-bold m-0">Consola de Proyectos</h2>
                <button class="btn btn-primary" onclick="app.showProjectModal()">+ Nuevo Proyecto</button>
            </div>
            <div class="row g-4">
                ${this.db.projects.map(p => `
                    <div class="col-md-6">
                        <div class="card p-3 h-100 border-start border-4 ${p.status === 'En ejecución' ? 'border-primary' : 'border-warning'}">
                            <div class="d-flex justify-content-between mb-2">
                                <h5 class="fw-bold mb-0">${p.name}</h5>
                                <span class="badge ${p.status === 'En ejecución' ? 'bg-primary' : 'bg-warning text-dark'}">${p.status}</span>
                            </div>
                            <div class="text-muted small mb-3">${p.client}</div>
                            <button class="btn btn-sm btn-primary mt-auto" onclick="app.renderProjectDetail(${p.id})">Gestionar</button>
                        </div>
                    </div>
                `).join('') || '<div class="col-12 p-5 text-center">No hay proyectos</div>'}
            </div>
        `;
    },

    renderProjectDetail(id) {
        const p = this.db.projects.find(x => x.id === id);
        const container = document.getElementById('view-container');
        document.getElementById('current-breadcrumb').textContent = p.name;

        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="fw-bold m-0">${p.name}</h3>
                <div>
                    ${p.status === 'Planificado' ? `<button class="btn btn-success" onclick="app.executeProject(${p.id})">Ejecutar</button>` : ''}
                    <button class="btn btn-outline-secondary" onclick="app.navigate('projects')">Volver</button>
                </div>
            </div>
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card p-4 border-0 shadow-sm mb-4">
                        <div class="d-flex justify-content-between mb-3">
                            <h5 class="fw-bold">Insumos</h5>
                            ${p.status === 'Planificado' ? `<button class="btn btn-sm btn-primary" onclick="app.showAddMatProj(${p.id})">+ Asignar</button>` : ''}
                        </div>
                        <table class="table">
                            <thead><tr><th>Material</th><th>Requerido</th><th>Estado</th></tr></thead>
                            <tbody>
                                ${p.materials.map(pm => {
            const m = this.db.materials.find(x => x.id === pm.material_id);
            const bug = m.quantity < pm.quantity;
            return `<tr class="${bug ? 'table-danger' : ''}"><td>${m.name}</td><td>${pm.quantity}</td><td>${bug ? 'Insuficiente' : 'OK'}</td></tr>`;
        }).join('') || '<tr><td colspan="3" class="text-center">Sin insumos</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card p-4 border-0 shadow-sm">
                        <h5 class="fw-bold mb-3">Cliente</h5>
                        <p>${p.client}</p>
                        <h5 class="fw-bold mb-1">Fecha</h5>
                        <p>${p.start_date}</p>
                    </div>
                </div>
            </div>
        `;
    },

    renderReports(container) {
        container.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="fw-bold m-0">Reportes y Auditoría</h2>
                <button class="btn btn-danger" onclick="app.generatePDF()"><i class="bi bi-file-pdf"></i> Exportar PDF</button>
            </div>
            <div class="card border-0 shadow-sm p-4">
                <h5 class="fw-bold mb-3">Historial de Actividad</h5>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead class="bg-light"><tr><th>Usuario</th><th>Acción</th><th>Fecha</th></tr></thead>
                        <tbody>
                            ${this.db.activity.slice().reverse().map(a => `
                                <tr><td>${a.user}</td><td>${a.action}</td><td>${a.timestamp}</td></tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    },

    renderTrash(container) {
        const deleted = this.db.materials.filter(m => m.is_deleted);
        container.innerHTML = `
            <h2 class="fw-bold mb-4">Papelera</h2>
            <div class="card border-0 shadow-sm overflow-hidden">
                <table class="table align-middle">
                    <thead class="bg-light"><tr><th>Nombre</th><th>Acciones</th></tr></thead>
                    <tbody>
                        ${deleted.map(m => `
                            <tr>
                                <td>${m.name}</td>
                                <td>
                                    <button class="btn btn-sm btn-success" onclick="app.restoreMaterial(${m.id})">Restaurar</button>
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="2" class="text-center p-4">Vacío</td></tr>'}
                    </tbody>
                </table>
            </div>
        `;
    },

    // --- MODALS ---
    showMaterialModal(id = null) {
        const m = id ? this.db.materials.find(x => x.id === id) : { name: '', quantity: 0, min_stock: 0, unit: 'Lts', supplier: '' };
        const html = `
            <div class="modal fade" id="matModal"><div class="modal-dialog"><div class="modal-content">
                <div class="modal-header fw-bold border-0">${id ? 'Editar' : 'Nuevo'} Material</div>
                <div class="modal-body">
                    <form id="mat-form">
                        <input type="text" name="name" class="form-control mb-3" value="${m.name}" placeholder="Nombre" required>
                        <div class="row g-2 mb-3">
                            <div class="col"><input type="number" name="quantity" class="form-control" value="${m.quantity}" placeholder="Cant" required></div>
                            <div class="col"><input type="number" name="min_stock" class="form-control" value="${m.min_stock}" placeholder="Min" required></div>
                        </div>
                        <input type="text" name="supplier" class="form-control mb-3" value="${m.supplier}" placeholder="Proveedor" required>
                        <button class="btn btn-primary w-100">Guardar</button>
                    </form>
                </div>
            </div></div></div>
        `;
        document.getElementById('modal-container').innerHTML = html;
        const modal = new bootstrap.Modal(document.getElementById('matModal'));
        modal.show();
        document.getElementById('mat-form').onsubmit = (e) => {
            e.preventDefault();
            const d = Object.fromEntries(new FormData(e.target));
            if (id) {
                const idx = this.db.materials.findIndex(x => x.id === id);
                this.db.materials[idx] = { ...this.db.materials[idx], ...d, quantity: parseFloat(d.quantity), min_stock: parseFloat(d.min_stock) };
            } else {
                this.db.materials.push({ id: Date.now(), ...d, quantity: parseFloat(d.quantity), min_stock: parseFloat(d.min_stock), unit: 'Unid', is_deleted: false });
            }
            this.saveDB(); modal.hide(); this.navigate('inventory');
        };
    },

    showProjectModal() {
        const html = `<div class="modal fade" id="projModal"><div class="modal-dialog"><div class="modal-content"><div class="modal-body">
            <h5 class="fw-bold mb-3">Nuevo Proyecto</h5>
            <form id="proj-form">
                <input type="text" name="name" class="form-control mb-2" placeholder="Nombre" required>
                <input type="text" name="client" class="form-control mb-2" placeholder="Cliente" required>
                <input type="date" name="start_date" class="form-control mb-3" required>
                <button class="btn btn-primary w-100">Crear</button>
            </form>
        </div></div></div></div>`;
        document.getElementById('modal-container').innerHTML = html;
        const modal = new bootstrap.Modal(document.getElementById('projModal'));
        modal.show();
        document.getElementById('proj-form').onsubmit = (e) => {
            e.preventDefault();
            const d = Object.fromEntries(new FormData(e.target));
            this.db.projects.push({ ...d, id: Date.now(), status: 'Planificado', materials: [], logs: [] });
            this.saveDB(); modal.hide(); this.navigate('projects');
        };
    },

    showAddMatProj(pid) {
        const activeMats = this.db.materials.filter(m => !m.is_deleted);
        const html = `<div class="modal fade" id="ampModal"><div class="modal-dialog"><div class="modal-content"><div class="modal-body">
            <h5 class="fw-bold mb-3">Asignar Insumo</h5>
            <form id="amp-form">
                <select name="material_id" class="form-select mb-2">
                    ${activeMats.map(m => `<option value="${m.id}">${m.name} (Disp: ${m.quantity})</option>`).join('')}
                </select>
                <input type="number" name="quantity" class="form-control mb-3" placeholder="Cantidad" required>
                <button class="btn btn-primary w-100">Asignar</button>
            </form>
        </div></div></div></div>`;
        document.getElementById('modal-container').innerHTML = html;
        const modal = new bootstrap.Modal(document.getElementById('ampModal'));
        modal.show();
        document.getElementById('amp-form').onsubmit = (e) => {
            e.preventDefault();
            const d = Object.fromEntries(new FormData(e.target));
            const p = this.db.projects.find(x => x.id === pid);
            p.materials.push({ material_id: parseInt(d.material_id), quantity: parseFloat(d.quantity) });
            this.saveDB(); modal.hide(); this.renderProjectDetail(pid);
        };
    },

    // --- CORE LOGIC ---
    executeProject(id) {
        const p = this.db.projects.find(x => x.id === id);
        for (const pm of p.materials) {
            const m = this.db.materials.find(x => x.id === pm.material_id);
            if (m.quantity < pm.quantity) return alert(`Stock insuficiente: ${m.name}`);
        }
        if (confirm('¿Desea ejecutar? Esto descontará el stock.')) {
            p.materials.forEach(pm => {
                const materialRef = this.db.materials.find(x => x.id === pm.material_id);
                if (materialRef) {
                    materialRef.quantity = parseFloat((materialRef.quantity - pm.quantity).toFixed(2));
                }
            });
            p.status = 'En ejecución';
            this.saveDB(); this.renderProjectDetail(id);
        }
    },

    deleteMaterial(id) {
        if (this.currentUser.role === 'Operativo' && prompt('Clave Admin:') !== 'admin123') return;
        const idx = this.db.materials.findIndex(x => x.id === id);
        this.db.materials[idx].is_deleted = true;
        this.saveDB(); this.navigate('inventory');
    },

    restoreMaterial(id) {
        const idx = this.db.materials.findIndex(x => x.id === id);
        this.db.materials[idx].is_deleted = false;
        this.saveDB(); this.navigate('trash');
    },

    exportBackup() {
        const blob = new Blob([JSON.stringify(this.db, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'oscm_backup.json';
        a.click();
    },

    generatePDF() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        doc.setFontSize(22);
        doc.text("Ortiflex OSCM - Reporte de Inventario", 20, 20);
        doc.setFontSize(12);
        doc.text(`Generado el: ${new Date().toLocaleString()}`, 20, 30);

        const data = this.db.materials.filter(m => !m.is_deleted).map(m => [m.name, m.quantity, m.supplier]);
        doc.autoTable({
            startY: 40,
            head: [['Material', 'Stock', 'Proveedor']],
            body: data,
            theme: 'striped',
            headStyles: { fillColor: [0, 74, 153] }
        });

        doc.save("oscm_reporte_global.pdf");
    },

    bindEvents() {
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login(document.getElementById('username').value, document.getElementById('password').value);
        });
    }
};

document.addEventListener('DOMContentLoaded', () => app.init());
