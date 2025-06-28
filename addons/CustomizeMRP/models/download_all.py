from odoo import models
from odoo.exceptions import UserError
import os
import base64
import zipfile
import io

UPLOAD_DIR = '/mnt/odoo-product-files'

class DownloadFirstFile(models.TransientModel):
    _name = 'product.file.download.wizard'
    _description = 'Descargar el primer archivo de producto'

    #Descargar el archivo
    # def action_download_first_file(self):
    #     # Validar que exista el directorio
    #     if not os.path.exists(UPLOAD_DIR):
    #         raise UserError(f'La carpeta {UPLOAD_DIR} no existe.')

    #     files = os.listdir(UPLOAD_DIR)
    #     if not files:
    #         raise UserError('No hay archivos para descargar.')

    #     # Crear un ZIP en memoria
    #     zip_buffer = io.BytesIO()
    #     with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
    #         for filename in files:
    #             file_path = os.path.join(UPLOAD_DIR, filename)
    #             if os.path.isfile(file_path):
    #                 zip_file.write(file_path, arcname=filename)
    #     zip_buffer.seek(0)

    #     # Crear attachment para servir el archivo
    #     attachment = self.env['ir.attachment'].create({
    #         'name': 'archivos_productos.zip',
    #         'type': 'binary',
    #         'datas': base64.b64encode(zip_buffer.read()),
    #         'res_model': self._name,
    #         'res_id': self.id,
    #         'mimetype': 'application/zip',
    #     })

    #     # Devolver acción para descargar
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': f'/web/content/{attachment.id}?download=true',
    #         'target': 'new',
    #     }
    
    #Cargar el archivo
#  import os
# import base64
# import zipfile
# import io
# from odoo import models, fields, api
# import logging
# logger = logging.getLogger(__name__)

# # Ruta donde se guardarán los archivos dentro del contenedor
# UPLOAD_DIR = '/mnt/odoo-product-files'  # Esta ruta debe mapearse en Docker a una carpeta local

# class ProductFile(models.Model):
#     _name = 'product.file'
#     _description = 'Archivos de Producto'

#     product_id = fields.Many2one('product.product', string='Producto', required=True)
#     file_upload = fields.Binary(string='Archivo', required=True)  # Solo se usa temporalmente
#     file_name = fields.Char(string='Nombre del archivo', required=True)
#     file_path = fields.Char(string='Ruta en el sistema', readonly=True)

    # @api.model
    # def create(self, vals):
    #     binary_data = vals.pop('file_upload', False)
    #     original_filename = vals.get('file_name')

    #     if binary_data and original_filename:
    #         os.makedirs(UPLOAD_DIR, exist_ok=True)

    #         Nombre del archivo zip
    #         base_name, _ = os.path.splitext(original_filename)
    #         zip_filename = base_name + '.zip'
    #         zip_path = os.path.join(UPLOAD_DIR, zip_filename)

    #         Crear zip en memoria
    #         with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    #             zipf.writestr(original_filename, base64.b64decode(binary_data))

    #         vals['file_path'] = zip_path
    #         vals['file_name'] = zip_filename  # Opcional: reemplaza nombre por el zip

    #     return super().create(vals)
    
#     # @api.model
#     # def create(self, vals):
#     #     binary_data = vals.pop('file_upload', False)
#     #     filename = vals.get('file_name')

#     #     if binary_data and filename:
#     #         os.makedirs(UPLOAD_DIR, exist_ok=True)
#     #         file_path = os.path.join(UPLOAD_DIR, filename)

#     #         with open(file_path, 'wb') as f:
#     #             f.write(base64.b64decode(binary_data))

#     #         vals['file_path'] = file_path

#     #     return super().create(vals)


    

#     @api.depends('file_path')
#     def _compute_download_url(self):
#         for record in self:
#             if record.file_path:
#                 filename = os.path.basename(record.file_path)
#                 record.download_url = f'/web/content/product.file/{record.id}/download/{filename}'
#             else:
#                 record.download_url = ''