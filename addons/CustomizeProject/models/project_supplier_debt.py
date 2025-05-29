from odoo import models, fields

class ProjectSupplierDebt(models.Model):
    _name = 'project.supplier.debt'
    _description = 'Créditos de Proveedores por Proyecto'
    _order = 'fecha desc'

    project_id = fields.Many2one('project.project', string='Proyecto', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Proveedor', domain="[('supplier_rank', '>', 0)]", required=True)
    monto = fields.Float(string='Monto', required=True)
    fecha = fields.Date(string='Fecha del crédito', required=True, default=fields.Date.today)
    nota = fields.Text(string='Nota')
    tipo_trx = fields.Selection([
        ('abn', 'Abonar a Crédito'),
        ('Pre', 'Generar Préstamo')
    ], string='Tipo Transacción', default='Pre', required=True)
