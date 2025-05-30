from odoo import models, fields, api
from collections import defaultdict

class ProjectDashboardCommission(models.Model):
    _name = 'project.dashboard.commission'
    _description = 'Resumen Comisiones por Pagar'

    project_ids = fields.One2many('project.project', 'dashboard_commission_id', string='Proyectos')

    name = fields.Char(string='Nombre')
    total_commission = fields.Float(string='Total General de Cuentas por Pagar', compute='_compute_totals')
    total_by_vendor = fields.Text(string='Deuda por Vendedor', compute='_compute_totals')


    @api.depends('project_ids.commission_due', 'project_ids.partner_id_v')
    def _compute_totals(self):
        for record in self:
            vendor_totals = defaultdict(float)
            total = 0.0

            for project in record.project_ids:
                if project.partner_id_v:
                    vendor_totals[project.partner_id_v.name] += project.commission_due
                    total += project.commission_due

            record.total_commission = total

            # Crear texto tipo: "Juan Pérez: 1500.0\nMaría García: 2000.0"
            lines = [f"{vendor}: {amount:,.2f}" for vendor, amount in vendor_totals.items()]
            record.total_by_vendor = "\n".join(lines)
