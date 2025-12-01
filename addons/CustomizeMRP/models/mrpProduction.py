from odoo import models, fields, api, exceptions
import os
from odoo.exceptions import UserError
import base64
from datetime import datetime
import textwrap


import logging

logger = logging.getLogger(__name__)
UPLOAD_DIR = '/mnt/odoo-product-files'  # RUTA base
                           
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_order_id = fields.Many2one("sale.order", string="Cotización Relacionada")
    task_id = fields.Many2one('project.task', string="Tarea Relacionada")
    employee_id = fields.Many2one('hr.employee', string='Fabricante')
    description = fields.Text(string="Descripción del producto")
    frente = fields.Char(string="Frente")
    fondo = fields.Char(string="Fondo")
    altura = fields.Char(string="Altura")
    date_start_per = fields.Datetime(string="Último Timestamp")
    sale_line_id = fields.Many2one('sale.order.line', string='Línea de Venta', ondelete='set null' )
    zpl_temp = fields.Binary("Etiqueta ZPL")

    def action_start(self):
        if not self.employee_id :
            raise exceptions.UserError("Asigne el producto a fabricar a un responsable")
        self.ensure_one()
        stage = self.env["project.task.type"].search([("name", "=", "Fabricando")], limit=1)
        u_task_name = self.task_id.name + " - " + self.employee_id.name
        self.task_id.write({
            'stage_id': stage.id,
            'name':u_task_name
        }, cond=False)
        self.date_start_per = fields.Datetime.now()
        return super(MrpProduction, self).action_start()


    def button_mark_done(self):
        if self.state != 'progress':
            raise exceptions.UserError("Primero debe Poner a Fabricar el Producto")        
        self.ensure_one()
        stage = self.env["project.task.type"].search([("name", "=", "Terminado")], limit=1)
        self.task_id.write({
            'stage_id': stage.id
        }, cond=False)   
        return super(MrpProduction, self).button_mark_done()
    
    def action_open_design_module(self):
        self.ensure_one()
        design = self.env['product.file.design'].search([('production_id', '=', self.id)], limit=1)
        if not design:
            design = self.env['product.file.design'].create({
                'production_id': self.id,
                'project_id': self.project_id.id,
                'product_id': self.product_id.id,
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.file.design',
            'view_mode': 'form',
            'res_id': design.id,
            'target': 'current',
        }
    
    def action_open_plano(self):

        if not self.project_id.plano_loaded:
            raise UserError("No hay ningún plano cargado")
        
        path = os.path.join(UPLOAD_DIR, self.project_id.name or '', 'plano')
        logger.info(path)
        archivos = [f for f in os.listdir(path) if f.startswith("Plano")]
         # Por ejemplo, descarga el primero
        archivo = archivos[0]
        full_path = os.path.join(path, archivo)
        logger.info(full_path)
        if not archivos:
            raise UserError("No hay archivos disponibles.")


    # Leer y codificar el archivo
        with open(full_path, 'rb') as f:
            file_content = f.read()

        attachment = self.env['ir.attachment'].create({
            'name': archivo,
            'type': 'binary',
            'datas': base64.b64encode(file_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',  # o 'application/octet-stream'
        })

        # Descargar el archivo desde el attachment
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }

    @api.model
    def _escape_zpl(self, text):
        """Limpia caracteres que podrían romper el ZPL."""
        if not text:
            return ""
        text = text.replace("\n", " ").replace("\r", " ").replace("^", "").replace("~", "")
        return text
    def split_description_lines(self, text, max_chars=40):
        """
        Divide un texto largo en varias líneas sin cortar palabras.
        Retorna una lista de líneas adecuadas para ZPL (^FD).
        """

        if not text:
            return []

        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            # Si agregar la siguiente palabra excede el límite, se inicia una nueva línea
            if len(current_line) + len(word) + 1 > max_chars:
                lines.append(current_line)
                current_line = word
            else:
                current_line = word if current_line == "" else current_line + " " + word

        # Agregar la última línea
        if current_line:
            lines.append(current_line)

        return lines
    
    def action_etiqueta(self):
        self.ensure_one()

        # Datos
        production_id = str(self.id)
        product_name = self._escape_zpl(self.product_id.display_name)
        fabricante = self._escape_zpl(self.employee_id.name or "N/A")
        project_name = self._escape_zpl(
            self.sale_order_id.project_id.name if self.sale_order_id and self.sale_order_id.project_id else "N/A"
        )
        descripcion = self._escape_zpl(self.description or self.product_id.name)
        descripcion_lines = self.split_description_lines(descripcion, max_chars=40)

        # ZPL ajustado a etiqueta 100x50
        zpl = f"""
^XA
^CI28          ; UTF-8 / Unicode (si tu firmware lo soporta)
^PW800
^LL400
^LH0,0
^CF0,40

; --- Encabezado centrado usando bloque de ancho total (800) ---
^FO0,10^FB800,1,0,C,0
^A0N,42,42
^FDUniverso Gastronómico S.A.^FS

; --- Dejamos espacio vertical suficiente antes del resto ---
^FO40, 120^FDProyecto: {project_name}^FS
^FO40,180^FDProducto: {product_name}^FS
^FO40,240^FDOrden: {production_id}^FS
^FO40,300^FDFabricante: {fabricante}^FS
^XZ





        """


        # Guardar el ZPL en el campo binario para descarga
        self.zpl_temp = base64.b64encode(zpl.encode("utf-8"))

        # Acción de descarga
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self.id}?model=mrp.production&field=zpl_temp&filename={product_name}_{production_id}.prn&download=true",
            "target": "self",
        }
