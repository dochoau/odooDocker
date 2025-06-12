import os
import base64
from odoo import models, fields, api
from odoo.tools import config
from odoo.http import request
from odoo.exceptions import UserError

# Ruta donde se guardarán los archivos dentro del contenedor
UPLOAD_DIR = '/mnt/odoo-product-files'  # Esta ruta debe mapearse en Docker a una carpeta local

class ProductFile(models.Model):
    _name = 'product.file'
    _description = 'Archivos de Producto'

    product_id = fields.Many2one('product.product', string='Producto', required=True)
    file_upload = fields.Binary(string='Archivo', required=True)  # Solo se usa temporalmente
    file_name = fields.Char(string='Nombre del archivo', required=True)
    file_path = fields.Char(string='Ruta en el sistema', readonly=True)

    @api.model
    def create(self, vals):
        binary_data = vals.pop('file_upload', False)
        filename = vals.get('file_name')

        if binary_data and filename:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            file_path = os.path.join(UPLOAD_DIR, filename)

            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(binary_data))

            vals['file_path'] = file_path

        return super().create(vals)
    @api.depends('file_path')
    def _compute_download_url(self):
        for record in self:
            if record.file_path:
                filename = os.path.basename(record.file_path)
                record.download_url = f'/web/content/product.file/{record.id}/download/{filename}'
            else:
                record.download_url = ''

    def action_download_file(self):
        if not self.file_path:
            raise UserError('No hay un archivo disponible para descargar.')
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/product.file/{self.id}/download/{os.path.basename(self.file_path)}',
            'target': 'new',
        }