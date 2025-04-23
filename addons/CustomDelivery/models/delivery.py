from odoo import models
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)

class DeliveryWizard(models.TransientModel):
    _name = 'delivery.wizard'
    _description = 'Wizard de Entregado'

    def confirm_action(self, action_type):
        
        task = self.env['project.task'].browse(self.env.context.get('active_id'))

        if not task:
            raise UserError("Tarea no encontrada.")

        stage_entregado = self.env['project.task.type'].search([('name', '=', 'Entregado')], limit=1)

        if action_type == 'one':
            task.write({'stage_id': stage_entregado.id}, cond=False)
        elif action_type == 'all':
            tareas_terminadas = self.env['project.task'].search([
                ('project_id', '=', task.project_id.id),
                ('stage_id.name', '=', 'Instalación')
            ])
            for tarea in tareas_terminadas:
                tarea.write({'stage_id': stage_entregado.id}, cond=False)



    def action_instalar_equipo(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "¿Está seguro?",
            'res_model': 'delivery.confirmation',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, action_type='one'),
        }

    def action_instalar_todos(self):
        return {
            'type': 'ir.actions.act_window',
            'name': "¿Está seguro?",
            'res_model': 'delivery.confirmation',
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context, action_type='all'),
        }