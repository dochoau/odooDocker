import os
import base64
import zipfile
import io
from odoo import models, fields, api
import logging
from odoo.exceptions import UserError
import fnmatch


logger = logging.getLogger(__name__)

# Ruta donde se guardarán los archivos dentro del contenedor
UPLOAD_DIR = '/mnt/odoo-product-files'  # Esta ruta debe mapearse en Docker a una carpeta local

class ProductFile(models.Model):
    _name = 'product.file.design'
    _description = 'Archivos de Producto'

    #### Variables nuevo modelo
    production_id = fields.Many2one('mrp.production', string='Orden de Producción', required=True)
    project_id = fields.Many2one('project.project', string="Proyecto", store=True, readonly=True)
    product_id = fields.Many2one('product.product', string="Producto", store=True, readonly=True)

    dxf_loaded = fields.Boolean(string="DXF cargado", default=False)
    bom_loaded = fields.Boolean(string="Lista materiales cargada", default=False)
    instructions_loaded = fields.Boolean(string="Instructivo cargado", default=False)

    # Campos para cargar desde la interfaz
    dxf_file = fields.Binary(string="Archivo DXF")
    dxf_filename = fields.Char(string="Nombre archivo DXF")

    bom_file = fields.Binary(string="Archivo Lista Materiales")
    bom_filename = fields.Char(string="Nombre archivo BOM")

    instruction_file = fields.Binary(string="Archivo Instructivo")
    instruction_filename = fields.Char(string="Nombre archivo Instructivo")

    def _get_path(self):
        ruta = os.path.join(UPLOAD_DIR, self.project_id.name or '', self.production_id.name or '', self.product_id.name or '')
        logger.info(ruta)    
        return ruta
    
    def action_upload_dxf(self):
        self._save_file('dxf', self.dxf_file, self.dxf_filename)
        self.dxf_loaded = True

    def action_upload_bom(self):
        self._save_file('bom', self.bom_file, self.bom_filename)
        self.bom_loaded = True

    def action_upload_instruction(self):
        self._save_file('instruction', self.instruction_file, self.instruction_filename)
        self.instructions_loaded = True

    def _save_file(self, tipo, filedata, filename):
        orden_pdc = self.production_id.name.replace("/", "_")
        path = self._get_path()
        os.makedirs(path, exist_ok=True)
        file_content = base64.b64decode(filedata)
        file_path = os.path.join(path, f"{orden_pdc}_{tipo}_{filename}")
        # Escribir en disco
        with open(file_path, "wb") as f:
            f.write(file_content)

    def action_download_dxf(self):
        return self._download_zip('dxf')

    def action_download_bom(self):
        return self._download_zip('bom')

    def action_download_instruction(self):
        return self._download_zip('instruction')

    def _download_zip(self,tipo):
        """Buscar archivo por patrón {orden_pdc}_{tipo}_* en la misma ruta y descargarlo"""
        self.ensure_one()
        orden_pdc = self.production_id.name.replace("/", "_")
        path = self._get_path()

        # Construir patrón de búsqueda
        pattern = f"{orden_pdc}_{tipo}_*"

        # Buscar el archivo en la carpeta
        file_path = None
        for fname in os.listdir(path):
            if fnmatch.fnmatch(fname, pattern):
                file_path = os.path.join(path, fname)
                break

        if not file_path or not os.path.exists(file_path):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No encontrado",
                    "message": f"No se encontró ningún archivo con patrón {pattern}",
                    "sticky": False,
                },
            }

        # Leer archivo y crear attachment temporal
        with open(file_path, "rb") as f:
            file_content = f.read()

        attachment = self.env["ir.attachment"].create({
            "name": os.path.basename(file_path),
            "datas": base64.b64encode(file_content),
            "res_model": self._name,
            "res_id": self.id,
            "type": "binary",
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }


