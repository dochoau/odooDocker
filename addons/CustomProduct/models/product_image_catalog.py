from odoo import models, fields

class ProductImageCatalog(models.Model):
    _name = 'product.image.catalog'
    _description = 'Catálogo de Imágenes del Producto'

    name = fields.Char(string="Nombre", required=True)
    image = fields.Image(string="Imagen", required=True)
    product_tmpl_id = fields.Many2one(    'product.template',
    string='Producto',
    required=True,
    readonly=True,
    default=lambda self: self.env.context.get('default_product_id'))
    _rec_name = 'name'  # o cualquier campo representativo
    _preview = 'image'  