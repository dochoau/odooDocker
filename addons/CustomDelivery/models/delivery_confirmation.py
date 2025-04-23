from odoo import models
from odoo.exceptions import UserError

class DeliveryConfirmation(models.TransientModel):
    _name = 'delivery.confirmation'
    _description = 'Confirmación de Entregado'

    def action_confirm(self):
        wizard = self.env['delivery.wizard'].browse(self.env.context.get('active_id'))
        wizard.confirm_action(self.env.context.get('action_type'))