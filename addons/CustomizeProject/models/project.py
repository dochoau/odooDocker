from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    #Relaciona el proyecto con las ordenes de producción
    quotation_ids = fields.One2many('sale.order', 'project_id', string="Cotizaciones")
    
    #Relaciona el proyecto coon los clientes
    partner_id = fields.Many2one(
        'res.partner',  # Relación con la tabla de clientes
        string="Cliente",
        required=True,  # Opcional: si quieres que siempre se seleccione un cliente
        help="Cliente asociado a este proyecto."
    )
    last_stage = fields.Char(string='Última Etapa', readonly=True)



    #Sobre escribe el método Create
    def create(self, vals_list):
        """Sobrescribe create para agregar las etapas en un orden específico."""
        stage_model = self.env['project.task.type']
        
        # Definir las etapas necesarias con su secuencia
        stage_names = ['Cotizar', 'Por Fabricar', 'Fabricando', 'Terminado', 'Instalación', 'Entregado']
        stages = {}

        # Buscar o crear las etapas en el orden correcto
        for index, stage_name in enumerate(stage_names):
            stage = stage_model.search([('name', '=', stage_name)], limit=1)
            if not stage:
                stage = stage_model.create({
                    'name': stage_name,
                    'sequence': index  # Asegurar que se mantenga el orden correcto
                })
            else:
                # Si ya existe, aseguramos que la secuencia sea la correcta
                stage.write({'sequence': index}, cond = False)
            stages[stage_name] = stage

        # Crear los proyectos normalmente
        projects = super().create(vals_list)

        for project in projects:
            # Asociar las etapas al proyecto
            for stage in stages.values():
                stage.write({'project_ids': [(4, project.id)]}, cond = False)

            # Crear la tarea "Cotizar" en la etapa "Cotizar"
            self.env['project.task'].create({
                'name': 'Cotizar',
                'project_id': project.id,
                'stage_id': stages['Cotizar'].id  # Asignar a la etapa "Cotizar"
            }, cond = False)

        return projects

    def _update_project_stage_info(self):
            stage_order = ['Cotizar', 'Por Fabricar', 'Fabricando', 'Terminado', 'Instalación', 'Entregado']
            stage_color_map = {
                'Cotizar': 8,
                'Por Fabricar': 1,
                'Fabricando': 3,
                'Terminado': 7,
                'Instalación': 11,
                'Entregado': 10
            }

            for project in self:
                tasks = project.task_ids.filtered(lambda t: t.stage_id.name in stage_order)
                tasks_min = project.task_ids.filtered(lambda t: t.stage_id.name in stage_order and t.stage_id.name != 'Cotizar')

                # Buscar la etapa más avanzada
                most_advanced_task = max(
                    tasks, key=lambda t: stage_order.index(t.stage_id.name)
                )
                stage_name = most_advanced_task.stage_id.name

                # Buscar la etapa menos avanzada (índice más bajo)
                try:
                    least_advanced_task = min(
                        tasks_min, key=lambda t: stage_order.index(t.stage_id.name)
                    )

                    least_stage_name = least_advanced_task.stage_id.name

                except Exception as e:
                    pass


                

                status = ""
                if stage_name == "Cotizar":
                    status = "Cotizando"
                    color = 8
                elif stage_name == "Por Fabricar":
                    status = "Por Fabricar"
                    color = 1                    
                elif stage_name == "Fabricando"  :
                    status = "Fabricando"
                    color = 3                           
                elif stage_name == "Terminado" and  least_stage_name != "Terminado" :
                    status = "Fabricando"
                    color = 3                        
                elif stage_name == "Terminado" and  least_stage_name == "Terminado" :
                    status = "Terminado"
                    color = 7                      
                elif stage_name == "Instalación" and  least_stage_name in ("Por Fabricar", "Fabricando") :
                    status = "Instalando-Fabricando"
                    color = 11    
                elif stage_name == "Instalación" and  least_stage_name in ("Instalación", "Terminado") :
                    status = "Instalando"
                    color = 11    
                elif stage_name == "Entregado" and least_stage_name != "Entregado":
                    status = "Entregando"
                    color = 11    
                elif least_stage_name == "Entregado":
                    status = "Terminado"
                    color = 10

                project.write({
                    'color': color,
                    'last_stage': status                })
