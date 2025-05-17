from odoo import models, fields

class ProjectPayment(models.Model):
    _name = 'project.payment'
    _description = 'Pago del Proyecto'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    date = fields.Date(string='Fecha', default=fields.Date.context_today, required=True)
    amount = fields.Float(string='Monto del Pago', required=True)
    note = fields.Text(string='Notas')
