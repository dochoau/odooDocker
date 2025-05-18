# models/project_dashboard.py
from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)

class ProjectDashboardCartera(models.Model):
    _name = 'project.dashboard.cartera'
    _description = 'Totales de cartera agrupados por etapa'

    name = fields.Char(string='Nombre')
    total_general = fields.Float(string='Cartera Total', compute='_compute_totals', store=True)
    total_cotizando_fabricar = fields.Float(string='Por Producir', compute='_compute_totals', store=True)
    total_en_proceso = fields.Float(string='Produciendo', compute='_compute_totals', store=True)
    total_terminado = fields.Float(string='Entregado', compute='_compute_totals', store=True)
    project_ids = fields.One2many('project.project', 'dashboard_id', string='Proyectos')

    @api.depends('project_ids.amount_due', 'project_ids.last_stage', 'project_ids.payment_ids.amount')
    def _compute_totals(self):

        for record in self:
            all_projects = self.env['project.project'].search([])
            cotizando_fabricar = en_proceso = terminado = total = 0.0

            for proj in all_projects:
                total += proj.amount_due or 0.0
                stage = proj.last_stage
                if stage in ('Cotizando', 'Por Fabricar'):
                    cotizando_fabricar += proj.amount_due or 0.0
                if stage in ('Fabricando','Instalando','Terminado', 'Instalando-Fabricando', 'Entregando' ):
                    en_proceso += proj.amount_due or 0.0
                if stage == 'Proyecto Entregado Completamente':
                    terminado += proj.amount_due or 0.0

            record.total_general = total
            record.total_cotizando_fabricar = cotizando_fabricar
            record.total_en_proceso = en_proceso
            record.total_terminado = terminado
            
    
