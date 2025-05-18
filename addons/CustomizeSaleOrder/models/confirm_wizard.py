from odoo import models, fields

class SaleOrderConfirmWizard(models.TransientModel):
    _name = 'sale.order.confirm.wizard'
    _description = 'Confirmar Cotización con IVA o sin IVA'

    sale_order_id = fields.Many2one('sale.order', string='Cotización', required=True)
    opcion_iva = fields.Selection([
        ('con', 'Con IVA'),
        ('sin', 'Sin IVA')
    ], string='Opción de IVA', default='con', required=True)

    def confirmar(self):
        self.ensure_one()
        order = self.sale_order_id

        # Actualizar proyecto relacionado
        if order.project_id:
            if self.opcion_iva == 'con':
                # Si el total y el subtotal son iguales, asumimos que no se agregó IVA aún, así que lo calculamos
                if order.amount_total == order.amount_untaxed:
                    project_amount = order.amount_untaxed * 1.19
                else:
                    project_amount = order.amount_total
                order.project_id.amount_total = project_amount
                order.project_id.info_iva = "Proyecto con IVA"
            else:
                order.project_id.amount_total = order.amount_untaxed
                order.project_id.info_iva = "Proyecto sin IVA"
            order.project_id.amount_due = order.project_id.amount_total

        # Confirmar cotización
        order.action_confirm_original()

        #Crea la tarea para gestionar cartera
        stage = self.env["project.task.type"].search([("name", "=", "Cotizar")], limit=1)
        self.env["project.task"].create({
            "name": "Gestionar Cartera",
            "project_id": order.project_id.id,
            "stage_id": stage.id,
            "description": "Tarea para Gestionar Cartera",
            "amount_total": order.project_id.amount_total,
            "amount_due": order.project_id.amount_due,
            "info_iva": order.project_id.info_iva
        }, cond = False)
        
        #asignar a la cartera
        project = order.project_id
        # Buscar el dashboard existente o crear uno nuevo
        dashboard = self.env['project.dashboard.cartera'].search([], limit=1)
        if not dashboard:
            dashboard = self.env['project.dashboard.cartera'].create({
                'name': 'Dashboard General'
            })

        # Asignar el dashboard al proyecto
        project.dashboard_id = dashboard.id         
        
        return {'type': 'ir.actions.act_window_close'}
