from odoo import models, fields, api, exceptions
import logging

logger = logging.getLogger(__name__)
                           
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    sale_order_id = fields.Many2one("sale.order", string="Cotización Relacionada")
    task_id = fields.Many2one('project.task', string="Tarea Relacionada")
    employee_id = fields.Many2one('hr.employee', string='Fabricante')
    description = fields.Text(string="Descripción del producto")

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
            design = self.env['product.file.design'].create({'production_id': self.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.file.design',
            'view_mode': 'form',
            'res_id': design.id,
            'target': 'current',
        }