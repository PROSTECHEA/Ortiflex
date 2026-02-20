from fpdf import FPDF
import os

class OSCM_PDF(FPDF):
    def header(self):
        # Institutional Blue Header
        self.set_fill_color(0, 51, 102) # Dark Blue
        self.rect(0, 0, 210, 40, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 24)
        self.cell(0, 20, 'ORTIFLEX OSCM', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, 'Sistema de Gestión de Suministros e Inventario', 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Reporte generado automáticamente por OSCM', 0, 0, 'C')

def generate_project_report(project):
    pdf = OSCM_PDF()
    pdf.add_page()
    
    # Project Title
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, f'REPORTE DE PROYECTO: {project.name.upper()}', 0, 1, 'L')
    pdf.ln(5)
    
    # Metadata Table
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(45, 10, 'Estado:', 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 10, project.status, 1, 0, 'L')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(45, 10, 'Fecha Creación:', 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 10, project.date_created.strftime('%d/%m/%Y'), 1, 1, 'L')
    
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(45, 10, 'Inicio Ejecución:', 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 10, project.date_started.strftime('%d/%m/%Y %H:%M') if project.date_started else '-', 1, 0, 'L')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(45, 10, 'Finalización:', 1, 0, 'L', True)
    pdf.set_font('Arial', '', 10)
    pdf.cell(50, 10, project.date_ended.strftime('%d/%m/%Y %H:%M') if project.date_ended else '-', 1, 1, 'L')
    
    pdf.ln(10)
    
    # Description and Notes
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Descripción y Notas del Proyecto', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 8, txt=f"Descripción: {project.description or 'Sin descripción'}\n\nNotas Adicionales: {project.notes or 'Sin notas'}", border=1)
    
    pdf.ln(10)
    
    # Materials Table
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Insumos / Materiales Asignados', 0, 1, 'L')
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, 'Material', 1, 0, 'L', True)
    pdf.cell(45, 10, 'Cantidad Req.', 1, 0, 'C', True)
    pdf.cell(45, 10, 'Unidad', 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for pm in project.materials:
        if not pm.is_deleted:
            pdf.cell(100, 10, pm.material.name, 1, 0, 'L')
            pdf.cell(45, 10, str(pm.quantity_required), 1, 0, 'C')
            pdf.cell(45, 10, pm.material.unit, 1, 1, 'C')
            
    filename = f"report_project_{project.id}.pdf"
    path = os.path.join("app/static/reports", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf.output(path)
    return filename

def generate_inventory_report(materials):
    pdf = OSCM_PDF()
    pdf.add_page()
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'B', 18)
    pdf.cell(0, 10, 'REPORTE GLOBAL DE INVENTARIO', 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(0, 51, 102)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 10, "Material", 1, 0, 'L', True)
    pdf.cell(30, 10, "Stock", 1, 0, 'C', True)
    pdf.cell(40, 10, "Unidad", 1, 0, 'C', True)
    pdf.cell(40, 10, "Estado", 1, 1, 'C', True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for m in materials:
        if not m.is_deleted:
            status = "Bajo Stock" if m.quantity <= m.min_stock else "Optimo"
            pdf.cell(80, 10, m.name, 1, 0, 'L')
            pdf.cell(30, 10, str(m.quantity), 1, 0, 'C')
            pdf.cell(40, 10, m.unit, 1, 0, 'C')
            pdf.cell(40, 10, status, 1, 1, 'C')
        
    filename = "reporte_inventario_general.pdf"
    path = os.path.join("app/static/reports", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pdf.output(path)
    return filename
