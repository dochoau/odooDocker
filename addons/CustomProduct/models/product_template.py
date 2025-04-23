from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    image_catalog_ids = fields.One2many('product.image.catalog', 'product_tmpl_id', string="Catálogo de Imágenes")
