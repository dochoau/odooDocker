from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectSupplierDebtWizard(models.TransientModel):
    _name = 'project.supplier.debt.wizard'
    _description = 'Agregar Transacción de Crédito'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    partner_id = fields.Many2one('res.partner', string='Proveedor', domain="[('category_id.name', '=', 'Proveedor')]", required=True)
    tipo_trx = fields.Selection([
        ('Pre', 'Generar Préstamo'),
        ('abn', 'Abonar a Crédito')
    ], string='Tipo Transacción', required=True, default='Pre')
    monto = fields.Float(string='Monto', required=True)
    fecha = fields.Date(string='Fecha', default=fields.Date.today, required=True)
    nota = fields.Text(string='Nota')

    def action_confirm(self):
        self.ensure_one()

        if self.tipo_trx == 'abn':
            # Calcular cuánto se debe actualmente a este proveedor en el proyecto
            supplier_debts = self.env['project.supplier.debt'].search([
                ('project_id', '=', self.project_id.id),
                ('partner_id', '=', self.partner_id.id)
            ])
            deuda_actual = sum(d.monto if d.tipo_trx == 'Pre' else -d.monto for d in supplier_debts)

            if self.monto > deuda_actual:
                raise ValidationError(f"No puede abonar más de lo que se debe. Deuda actual con este proveedor: {deuda_actual:,.2f}")

        # Crear la transacción
        self.env['project.supplier.debt'].create({
            'project_id': self.project_id.id,
            'partner_id': self.partner_id.id,
            'tipo_trx': self.tipo_trx,
            'monto': self.monto,
            'fecha': self.fecha,
            'nota': self.nota,
        })

        return {'type': 'ir.actions.act_window_close'}
