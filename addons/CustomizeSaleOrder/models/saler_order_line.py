from odoo import models, fields
import logging
from PIL import Image, UnidentifiedImageError
import base64
import io

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

    def get_image_jpeg_base64(self):
        jpeg_base64 = self.product_id.image_1920.decode('utf-8')
        #logger.info(jpeg_base64)
        return jpeg_base64


    # def get_image_jpeg_base64(self):
    #     if not self.product_id.image_128:
    #         return False

    #     # Obtener la imagen en base64 (originalmente WebP)
    #     image_data = base64.b64decode(self.product_id.image_1920)


    #     try:
    #         # Abrir la imagen con PIL
    #         image = Image.open(io.BytesIO(image_data))
            
    #         # Convertir la imagen a RGB (necesario para guardar en JPEG)
    #         if image.mode != 'RGB':
    #             image = image.convert('RGB')
            
    #         # Guardar la imagen como JPEG en un buffer de memoria
    #         output = io.BytesIO()
    #         image.save(output, format='JPEG')
            
    #         # Codificar la imagen JPEG en base64
    #         jpeg_base64 = base64.b64encode(output.getvalue()).decode()
    #         return jpeg_base64
    #     except Exception as e:
    #         logger.error(f"Error convirtiendo la imagen a JPEG: {e}")
    #         return False