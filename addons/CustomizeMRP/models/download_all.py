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

    def action_download_first_file(self):
        # Validar que exista el directorio
        if not os.path.exists(UPLOAD_DIR):
            raise UserError(f'La carpeta {UPLOAD_DIR} no existe.')

        files = os.listdir(UPLOAD_DIR)
        if not files:
            raise UserError('No hay archivos para descargar.')

        # Crear un ZIP en memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for filename in files:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    zip_file.write(file_path, arcname=filename)
        zip_buffer.seek(0)

        # Crear attachment para servir el archivo
        attachment = self.env['ir.attachment'].create({
            'name': 'archivos_productos.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_buffer.read()),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/zip',
        })

        # Devolver acción para descargar
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }