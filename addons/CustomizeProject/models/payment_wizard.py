from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectPaymentWizard(models.TransientModel):
    _name = 'project.payment.wizard'
    _description = 'Wizard para registrar pago de proyecto'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    date = fields.Date(string='Fecha de Pago', required=True, default=fields.Date.context_today)
    amount = fields.Float(string='Monto del Pago', required=True)
    note = fields.Text(string='Notas')

    def action_confirm_payment(self):
        self.ensure_one()
        if self.amount > self.project_id.amount_due:
            raise ValidationError(
                f"El monto ingresado (${self.amount:,.2f}) excede la deuda pendiente del proyecto (${self.project_id.amount_due:,.2f})."
            )
        self.env['project.payment'].create({
            'project_id': self.project_id.id,
            'date': self.date,
            'amount': self.amount,
            'note': self.note,
        })
        return {'type': 'ir.actions.act_window_close'}
