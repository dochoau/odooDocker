from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectSupplierDebtWizard(models.TransientModel):
    _name = 'project.commission.debt.wizard'
    _description = 'Abonos a Comisiones'
    _order = 'fecha desc'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True, ondelete='cascade')
    partner_id_v = fields.Many2one('res.partner', string='Vendedor', domain="[('category_id.name', '=', 'Vendedor')]", required=True)
    abono = fields.Float(string='Abono Comisión', required=True)
    fecha = fields.Date(string='Fecha Abono', required=True, default=fields.Date.today)
    nota = fields.Text(string='Nota')


    def action_confirm(self):
        self.ensure_one()
        
        if self.abono > self.project_id.commission_due:
            raise ValidationError(
                f"El monto ingresado (${self.abono:,.2f}) excede el valor de la comisión pendiente (${self.project_id.commission_due:,.2f})."
            )
        self.env['project.commission.debt'].create({
            'project_id': self.project_id.id,
            'partner_id_v': self.partner_id_v.id,
            'fecha': self.fecha,
            'abono': self.abono,
            'nota': self.nota,
        })

        return {'type': 'ir.actions.act_window_close'}


