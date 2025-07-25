from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    image_catalog_ids = fields.One2many('product.image.catalog', 'product_tmpl_id', string="Catálogo de Imágenes")
    producto_tercerizado = fields.Boolean(string='Producto tercerizado')
    tipo_proceso = fields.Selection(
        selection=[
            ('frio', 'Frío'),
            ('coccion', 'Cocción'),
            ('extraccion', 'Extracción'),
            ('carpinteria', 'Carpintería'),
            ('log', 'Logística e Instalación')
        ],
        string='Tipo de Producto',
        required=True,
        default='carpinteria'
)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)

        # Impuesto con ID = 1
        tax = self.env['account.tax'].browse(1)
        if tax.exists():
            defaults['taxes_id'] = [(6, 0, [tax.id])]
            defaults['supplier_taxes_id'] = [(6, 0, [tax.id])]

        # Ruta de manufactura
        manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)

        if manufacture_route:
            defaults['route_ids'] = [(6, 0, [manufacture_route.id])]

        #Lo crea siempre como servicio
        defaults['type'] = 'service'

        return defaults