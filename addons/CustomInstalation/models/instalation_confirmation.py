from odoo import models
from odoo.exceptions import UserError

class InstallationConfirmation(models.TransientModel):
    _name = 'installation.confirmation'
    _description = 'Confirmación de Instalación'

    def action_confirm(self):
        wizard = self.env['installation.wizard'].browse(self.env.context.get('active_id'))
        wizard.confirm_action(self.env.context.get('action_type'))