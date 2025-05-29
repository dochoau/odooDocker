from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleOrderConfirmWizard(models.TransientModel):
    _name = 'sale.order.confirm.wizard'
    _description = 'Confirmar Cotización con IVA o sin IVA'

    sale_order_id = fields.Many2one('sale.order', string='Cotización', required=True)
    opcion_iva = fields.Selection([
        ('con', 'Con IVA'),
        ('sin', 'Sin IVA'),
        ('aiu', 'AIU')
    ], string='Opción de IVA', default='con', required=True)
    valor_impuesto_aiu = fields.Float(string='Valor del Impuesto (AIU)')
    commission = fields.Float(string = 'Comisión por la Venta')

    @api.constrains('opcion_iva', 'valor_impuesto_aiu')
    def _check_valor_impuesto_aiu(self):
        for wizard in self:
            if wizard.opcion_iva == 'aiu' and not wizard.valor_impuesto_aiu:
                raise ValidationError("Debe ingresar el valor del impuesto AIU.")

    def confirmar(self):
        self.ensure_one()
        order = self.sale_order_id

        if order.project_id:
            if self.opcion_iva == 'con':
                if order.amount_total == order.amount_untaxed:
                    project_amount = order.amount_untaxed * 1.19
                else:
                    project_amount = order.amount_total
                order.project_id.amount_total = project_amount
                order.project_id.info_iva = "Proyecto con IVA"

            elif self.opcion_iva == 'sin':
                order.project_id.amount_total = order.amount_untaxed
                order.project_id.info_iva = "Proyecto sin IVA"

            elif self.opcion_iva == 'aiu':
                # Validación extra por seguridad
                if not self.valor_impuesto_aiu:
                    raise ValidationError("Debe ingresar el valor del impuesto AIU.")
                order.project_id.amount_total = order.amount_untaxed * (1 + (self.valor_impuesto_aiu/100))
                order.project_id.info_iva = f"Proyecto con AIU ({self.valor_impuesto_aiu :.2f}%)"

            order.project_id.amount_due = order.project_id.amount_total
            order.project_id.commission = self.commission
            order.project_id.supplier_debt = 0

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
        # Buscar el dashboard existente o crear uno nuevo de cartera
        dashboard = self.env['project.dashboard.cartera'].search([], limit=1)
        if not dashboard:
            dashboard = self.env['project.dashboard.cartera'].create({
                'name': 'Dashboard General'
            })

        # Asignar el dashboard al proyecto
        project.dashboard_id = dashboard.id

        # Buscar el dashboard existente o crear uno nuevo de cuentas por pagar
        dashboard_debt = self.env['project.dashboard.debt'].search([], limit=1)
        if not dashboard_debt:
            dashboard_debt = self.env['project.dashboard.debt'].create({
                'name': 'Dashboard General Cuentas por Pagar'
            })

        # Asignar el dashboard al proyecto
        project.dashboard_debt_id = dashboard_debt.id

        #Crea la tarea para gestionar créditos a proveedors
        stage = self.env["project.task.type"].search([("name", "=", "Cotizar")], limit=1)
        self.env["project.task"].create({
            "name": "Gestionar Crédito Proveedores",
            "project_id": order.project_id.id,
            "stage_id": stage.id,
            "description": "Tarea para Gestionar Crédito a Proveedores",
            "supplier_debt": 0
        }, cond = False)         
        
        return {'type': 'ir.actions.act_window_close'}
