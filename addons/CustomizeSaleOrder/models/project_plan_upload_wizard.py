# wizards/project_plan_upload_wizard.py
import os
import base64
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
import zipfile

logger = logging.getLogger(__name__)

UPLOAD_DIR = '/mnt/odoo-product-files'  # RUTA base

class ProjectPlanUploadWizard(models.TransientModel):
    _name = 'project.plan.upload.wizard'
    _description = 'Cargar Plano del Proyecto'

    project_id = fields.Many2one('project.project', string="Proyecto", required=True)
    pdf_file = fields.Binary(string="Archivo PDF")
    filename_arch = fields.Char(string="Nombre del Archivo")

    def action_upload_plan(self):
        self.ensure_one()
        if not self.pdf_file :
            raise UserError("Debe adjuntar un archivo PDF válido.")
        
        self.filename_arch ="Plano.pdf"
        if not self.filename_arch.lower().endswith('.pdf'):
            raise UserError("El archivo debe ser un PDF.")

        project_folder = os.path.join(UPLOAD_DIR, self.project_id.name or '', 'plano')
        os.makedirs(project_folder, exist_ok=True)

        file_path = os.path.join(project_folder, self.filename_arch)
        # with open(file_path, 'wb') as f:
        #     f.write(base64.b64decode(self.pdf_file))


        zip_filename = 'Plano.zip'
        original_filename=self.filename_arch

        file_path_zip = os.path.join(project_folder, zip_filename)

        #Crear zip en memoria
        with zipfile.ZipFile(file_path_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(original_filename, base64.b64decode(self.pdf_file))

        return {'type': 'ir.actions.act_window_close'}
