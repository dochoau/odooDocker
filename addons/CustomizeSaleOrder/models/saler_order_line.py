from odoo import models, fields
import logging


logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    custom_description = fields.Text(
        string="Descripción del producto",
        help="Descripción personalizada para esta línea de producto."
    )

    product_image_field = fields.Image(
        string="Product Image",
        compute="_compute_product_image",
        store=True,
    )
