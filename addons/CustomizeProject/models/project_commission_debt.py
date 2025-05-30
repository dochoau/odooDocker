from odoo import models, fields

class ProjectCommissionDebt(models.Model):
    _name = 'project.commission.debt'
    _description = 'Abonos a Comisiones'
    _order = 'fecha desc'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True, ondelete='cascade')
    partner_id_v = fields.Many2one('res.partner', string='Vendedor', domain="[('category_id.name', '=', 'Vendedor')]", required=True)
    abono = fields.Float(string='Abono Comisión', required=True)
    fecha = fields.Date(string='Fecha Abono', required=True, default=fields.Date.today)
    nota = fields.Text(string='Nota')

