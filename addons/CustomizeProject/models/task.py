from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError
import logging

logger = logging.getLogger(__name__)

class ProjectTask(models.Model):
    _inherit = 'project.task'

    #Genera la marca de tarea por defecto
    is_default_task = fields.Boolean(string="Tarea por defecto", default=False)
    control_arrastre = fields.Boolean(string="TControla que no muevan las tareas", default=True)

    #Crea la relación entre la tarea y las cotizaciones y ordenes de producción
    sale_order_id = fields.Many2one('sale.order', string="Cotización")
    manufacturing_order_id = fields.Many2one('mrp.production', string="Orden de Producción")

    def create(self, vals, cond = True):
        """Evita la creación de tareas que no cumplan con las condiciones"""

        cotizar_stage = self.env['project.task.type'].search([('name', '=', 'Cotizar')], limit=1)
        por_fabricar_stage = self.env['project.task.type'].search([('name', '=', 'Por Fabricar')], limit=1)
        fabricando_stage = self.env['project.task.type'].search([('name', '=', 'Fabricando')], limit=1)
        terminado_stage = self.env['project.task.type'].search([('name', '=', 'Terminado')], limit=1)
        instalacion_stage = self.env['project.task.type'].search([('name', '=', 'Instalación')], limit=1)
        entregado_stage = self.env['project.task.type'].search([('name', '=', 'Entregado')], limit=1)

        if not vals.get('stage_id'): 
            raise exceptions.UserError(("No puede crear nuevas tareas en esta étapa"))   

        if vals.get('stage_id') == cotizar_stage.id and cond:
            if vals.get('name') != 'Cotizar':
                raise exceptions.UserError(("Solo se pueden crear cotizaciones"))
        
        if vals.get('stage_id') == por_fabricar_stage.id and cond:
            raise exceptions.UserError(("No puede crear nuevas ordenes de producción"))
 
        if vals.get('stage_id') == fabricando_stage.id and cond:
            raise exceptions.UserError(("No puede crear nuevas ordenes de producción"))       

        if vals.get('stage_id') == terminado_stage.id and cond:
            raise exceptions.UserError(("No puede crear nuevas tareas en esta étapa"))      

        if vals.get('stage_id') == instalacion_stage.id and cond:
            raise exceptions.UserError(("No puede crear nuevas tareas en esta étapa"))   
           
        if vals.get('stage_id') == entregado_stage.id and cond:
            raise exceptions.UserError(("No puede crear nuevas tareas en esta étapa"))                              

        #Asignar color dependiendo de la tarea

        if vals.get('stage_id') == cotizar_stage.id:
            vals['color'] = 8
        elif vals.get('stage_id') == por_fabricar_stage.id:
            vals['color'] = 1
        elif vals.get('stage_id') == fabricando_stage.id:
            vals['color'] = 3
        elif vals.get('stage_id') == terminado_stage.id:
            vals['color'] = 7
        elif vals.get('stage_id') == instalacion_stage.id:
            vals['color'] = 11
        elif vals.get('stage_id') == entregado_stage.id:
            vals['color'] = 10
        
        #Actualiza el color del proyecto
        task = super().create(vals) 
        task.project_id._update_project_stage_info()
        return task

    def write(self, vals, cond=True):

        if 'active' in vals and vals['active'] is False:
            raise UserError(("No está permitido archivar tareas."))    
        
        cotizar_stage = self.env['project.task.type'].search([('name', '=', 'Cotizar')], limit=1)
        por_fabricar_stage = self.env['project.task.type'].search([('name', '=', 'Por Fabricar')], limit=1)
        fabricando_stage = self.env['project.task.type'].search([('name', '=', 'Fabricando')], limit=1)
        terminado_stage = self.env['project.task.type'].search([('name', '=', 'Terminado')], limit=1)
        instalacion_stage = self.env['project.task.type'].search([('name', '=', 'Instalación')], limit=1)
        entregado_stage = self.env['project.task.type'].search([('name', '=', 'Entregado')], limit=1)

        for task in self:
            if task.is_default_task and any(field in vals for field in ['name', 'project_id']):
                raise exceptions.UserError("No puedes modificar una tarea predefinida.")
            
            #Evita que arraste la tarea
            if 'stage_id' in vals and cond:  # Verifica si se intenta cambiar la etapa
                raise exceptions.UserError("No puedes mover tareas entre etapas.")
            
        if vals.get('stage_id') == cotizar_stage.id:
            vals['color'] = 8
        elif vals.get('stage_id') == por_fabricar_stage.id:
            vals['color'] = 1
        elif vals.get('stage_id') == fabricando_stage.id:
            vals['color'] = 3
        elif vals.get('stage_id') == terminado_stage.id:
            vals['color'] = 7
        elif vals.get('stage_id') == instalacion_stage.id:
            vals['color'] = 11
        elif vals.get('stage_id') == entregado_stage.id:
            vals['color'] = 10

        #Actualiza el color del proyecto
        task = super().write(vals) 
        for task_u in self:
            task_u.project_id._update_project_stage_info()
        return task
            

    #Activar esta función para que a futuro no se puedan borrar tareas creadas
    # def unlink(self):
    #     for task in self:
    #         if task.is_default_task:
    #             raise exceptions.UserError("No puedes eliminar una tarea predefinida.")
    #     return super().unlink()


    def open_related_document(self):
        """ Abre la cotización o la orden de producción asociada a la tarea, si existe. 
            - Si la tarea está en la etapa 'Cotización' y tiene una cotización asignada → Abre la cotización.  
            - Si la tarea está en 'Cotización' pero no tiene cotización → Abre la pantalla de nueva cotización.  
            - Si la tarea tiene una orden de producción asignada → Abre la orden de producción.  
            - Si no tiene ninguna de las anteriores → Muestra un mensaje.  
        """
        self.ensure_one()

        # Obtener el nombre del stage en el que está la tarea
        stage_name = self.stage_id.name.lower()
        if stage_name == "cotizar":
            if self.sale_order_id:
                return {
                    'name': "Cotización",
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order',
                    'view_mode': 'form',
                    'target': 'current',
                    'res_id': self.sale_order_id.id,
                    'force_context': True
                }
            else:
                return {
                    'name': "Crear Cotización",
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order',
                    'view_mode': 'form',
                    'target': 'current',
                    'context': {
                        'default_partner_id': self.partner_id.id, 
                        'default_project_id': self.project_id.id,
                        'default_project_name': self.project_id.name,  
                        'default_task_id': self.id,
                        'force_context': True
                    },
                }

        elif stage_name == "por fabricar":
            return {
                'name': "Orden de Producción",
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'res_id': self.manufacturing_order_id.id,
                'force_context': True
            }
        elif stage_name == "fabricando":
            return {
                'name': "Orden de Producción",
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.production',
                'view_mode': 'form',
                'res_id': self.manufacturing_order_id.id,
                'force_context': True
            }
        elif stage_name == "terminado":
            return {
                'name': ('Iniciar Proceso de Instalación'),
                'type': 'ir.actions.act_window',
                'res_model': 'installation.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'active_id': self.id,
                    'active_model': 'project.task',
                }
            }
        elif stage_name == "instalación":
            return {
                'name': ('Iniciar Proceso de Instalación'),
                'type': 'ir.actions.act_window',
                'res_model': 'delivery.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'active_id': self.id,
                    'active_model': 'project.task',
                }
            }    
        else:
            raise UserError("No hay documentos asociados a esta tarea.")
############Pendiente qué hacer con el botón de la última tarea############################
        


