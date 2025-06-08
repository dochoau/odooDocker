from odoo import models, fields, api, exceptions
import logging


logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    project_id = fields.Many2one('project.project', string="Proyecto")
    task_id = fields.Many2one('project.task', string="Tarea Relacionada")
    has_created_production_orders = fields.Boolean(
        string="Órdenes de Producción Creadas", 
        default=False
    )

    @api.model_create_multi
    def create(self, vals):
        if isinstance(vals, list):  # Si recibe una lista (varias cotizaciones)
            for val in vals:
                if val.get("task_id"):
                    task = self.env["project.task"].browse(val["task_id"])
                    val["partner_id"] = task.partner_id.id  # Asignar cliente de la tarea
                    val["task_id"] = task.id  # Asegurar que task_id se asigne en la cotización
                    val["project_id"] = task.project_id.id
                    project = self.env["project.project"].browse(vals["project_id"])
                    val["project_id"] = project.id

            sale_orders = super(SaleOrder, self).create(vals)  # Crear cotizaciones

            
            for order in sale_orders:
                if order.task_id:
                    order.task_id.sale_order_id = order.id  # Asignar la cotización a la tarea

            logger.info("Se ejecutó el create")
            return sale_orders

        
    def action_create_production_orders(self):
        """ Crea órdenes de producción y tareas en el proyecto asignado """
        if self.state == 'draft':
            raise exceptions.UserError(("Primero Confirma la Cotización"))
        stage = self.env["project.task.type"].search([("name", "=", "Por Fabricar")], limit=1)
        stage_terminado = self.env["project.task.type"].search([("name", "=", "Terminado")], limit=1)

        if self.has_created_production_orders:
            raise exceptions.UserError(("Ya se creó las ordenes de producción"))

 
        #Obtener el nombre del proyecto
        project_name = self.project_id.name
        for line in self.order_line:
            qty = int(line.product_uom_qty)
            self.has_created_production_orders = True
            if not line.product_id:
                continue
            
            for i in range(qty):
                # Crear la orden de producción
                if line.product_id.producto_tercerizado:
                    task = self.env["project.task"].create({
                        "name": f"{project_name} - {line.product_id.display_name}({i+1})",
                        "project_id": self.project_id.id,
                        "stage_id": stage_terminado.id,
                        "description": "Producto Tercerizado o Logística"
                    }, cond = False)
                else:
                    production_order = self.env["mrp.production"].create({
                        "product_id": line.product_id.id,
                        "product_qty": 1,
                        "sale_order_id": self.id,
                        "origin" : project_name,
                        "description" : line.custom_description                })

                    # Crear la tarea en el proyecto asociado
                    
                    task = self.env["project.task"].create({
                        "name": f"{project_name} - {line.product_id.display_name}({i+1})",
                        "project_id": self.project_id.id,
                        "stage_id": stage.id,
                        "description": f"Orden de producción creada: {production_order.name}",
                        "manufacturing_order_id" : production_order.id
                    }, cond = False)
                    production_order.task_id = task.id
                    production_order.state ="confirmed"


    def action_ver_reporte_html(self):
        self.ensure_one()

        for line in self.order_line:
             if line.product_id and line.product_id.image_1920:
                line.write({
                    'product_image_field': line.product_id.image_1920
                })


        # return {
        #     'type': 'ir.actions.report',
        #     'report_name': 'CustomizeSaleOrder.report_saleorder_custom_html',
        #     'report_type': 'qweb-pdf',
        #     'report_file': 'CustomizeSaleOrder.report_saleorder_custom_html',
        #     'name': 'Cotización - %s' % (self.name),
        # }
        return {
            'type': 'ir.actions.act_url',
            'url': f'/report/html/CustomizeSaleOrder.report_saleorder_custom_html_nopdf/{self.id}',
            'target': 'new',
        }

    def action_confirm(self):
        self.ensure_one()
        return {
            'name': 'Confirmar Cotización',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.confirm.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }

    def action_confirm_original(self):
        """Método original de confirmación (guardado para ser llamado desde el wizard)"""
        return super(SaleOrder, self).action_confirm()