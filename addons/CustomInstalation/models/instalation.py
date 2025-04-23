from odoo import models
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)

class InstallationWizard(models.TransientModel):
    _name = 'installation.wizard'
    _description = 'Wizard de Instalación'

    def confirm_action(self, action_type):
        
        task = self.env['project.task'].browse(self.env.context.get('active_id'))

        if not task:
            raise UserError("Tarea no encontrada.")

        stage_instalando = self.env['project.task.type'].search([('name', '=', 'Instalación')], limit=1)

        if action_type == 'one':
            task.write({'stage_id': stage_instalando.id}, cond=False)
        elif action_type == 'all':
            tareas_terminadas = self.env['project.task'].search([
                ('project_id', '=', task.project_id.id),
                ('stage_id.name', '=', 'Terminado')
            ])
            for tarea in tareas_terminadas:
                tarea.write({'stage_id': stage_instalando.id}, cond=False)



    def action_instalar_equipo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "¿Está seguro?",
            'res_model': 'installation.confirmation',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, action_type='one'),
        }

    def action_instalar_todos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "¿Está seguro?",
            'res_model': 'installation.confirmation',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, action_type='all'),
        }