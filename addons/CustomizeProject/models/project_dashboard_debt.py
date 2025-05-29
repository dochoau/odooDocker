from odoo import models, fields, api

class ProjectDashboardDebt(models.Model):
    _name = 'project.dashboard.debt'
    _description = 'Resumen de Cuentas por Pagar de Proyectos'

    project_ids = fields.One2many('project.project', 'dashboard_debt_id', string='Proyectos')

    name = fields.Char(string='Nombre')
    total_debt = fields.Float(string='Total General de Cuentas por Pagar', compute='_compute_totals')
    total_by_supplier = fields.Text(string='Deuda por Proveedor', compute='_compute_totals')

    @api.depends('project_ids.supplier_debt', 'project_ids.supplier_debt_ids')
    def _compute_totals(self):
        for record in self:
            # Total deuda por todos los proyectos
            record.total_debt = sum(record.project_ids.mapped('supplier_debt'))

            # Deuda agrupada por proveedor
            deuda_proveedores = {}
            for trx in record.project_ids.mapped('supplier_debt_ids'):
                proveedor = trx.partner_id.name
                deuda_proveedores.setdefault(proveedor, 0.0)

                if trx.tipo_trx == 'Pre':
                    deuda_proveedores[proveedor] += trx.monto
                elif trx.tipo_trx == 'abn':
                    deuda_proveedores[proveedor] -= trx.monto

            # Formatear para vista (excluyendo deudas cero si se desea)
            texto = '\n'.join([
                f"{prov}: ${monto:,.2f}"
                for prov, monto in deuda_proveedores.items()
                if abs(monto) > 0.001
            ])
            record.total_by_supplier = texto
