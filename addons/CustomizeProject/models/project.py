from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    #Relaciona el proyecto con las ordenes de producción
    quotation_ids = fields.One2many('sale.order', 'project_id', string="Cotizaciones")
    
    #Relaciona el proyecto coon los clientes
    partner_id = fields.Many2one(
        'res.partner',  # Relación con la tabla de clientes
        string="Cliente",
        required=True,  # Opcional: si quieres que siempre se seleccione un cliente
        help="Cliente asociado a este proyecto."
    )
    #Estados del proyecto
    last_stage = fields.Char(string='Última Etapa', readonly=True)
    estado_final = fields.Char(string='Estado Final', compute='_compute_estado_final', store=True)
    
    #Valor de la comisión
    commission = fields.Float(string = 'Comisión por la Venta (%)')
    commission_money = fields.Float(string = 'Comisión por la Venta ($)')
    commission_due = fields.Float(string = 'Valor Pendiente Comisión', compute='_compute_commision_due', store=True)
    partner_id_v = fields.Many2one('res.partner', string='Vendedor', domain="[('category_id.name', '=', 'Vendedor')]", required = True)
    commission_debt_ids = fields.One2many(
    'project.commission.debt', 'project_id', string='Abonos a Comisión Vendedores'
    )
    dashboard_commission_id = fields.Many2one('project.dashboard.commission', string='Dashboard de Comisiones')
  
    #Deudas a Proveedores
    supplier_debt = fields.Float(string = 'Cuentas por Pagar', compute='_compute_supplier_debt', store=True)
    supplier_debt_ids = fields.One2many(
    'project.supplier.debt', 'project_id', string='Créditos de Proveedores'
    )
    resumen_deuda_proveedores = fields.Text(string='Deuda por Proveedor', compute='_compute_resumen_deuda_proveedores')
    dashboard_debt_id = fields.Many2one('project.dashboard.debt', string='Dashboard de Deuda')

    #Información sobre valor del proyecto
    amount_total_untaxed = fields.Float(string = 'Valor Proyecto sin Impuestos')
    amount_total = fields.Float(string = 'Valor Vendido')
    amount_due =  fields.Float(string = 'Valor Pendiente', compute='_compute_amount_due', store=True)
    info_iva = fields.Char()

    payment_ids = fields.One2many('project.payment', 'project_id', string='Pagos')
    dashboard_id = fields.Many2one('project.dashboard.cartera', string='Dashboard')

    #Generar el valor de la deuda
    @api.depends('amount_total', 'payment_ids.amount')
    def _compute_amount_due(self):
        for project in self:
            total_paid = sum(project.payment_ids.mapped('amount'))
            project.amount_due = project.amount_total - total_paid
            if project.amount_due <= 0 and project.dashboard_id:
                project.dashboard_id = False
            
            # Buscar la tarea "Gestionar Cartera"
            cartera_task = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('name', 'ilike', 'Gestionar Cartera')
            ], limit=1)

            if cartera_task:
                cartera_task.amount_due = project.amount_due
    
    #Calcular Deuda por proveedor
    @api.depends('supplier_debt_ids')
    def _compute_resumen_deuda_proveedores(self):
        for project in self:
            resumen = {}
            for debt in project.supplier_debt_ids:
                partner = debt.partner_id
                if partner not in resumen:
                    resumen[partner] = 0
                resumen[partner] += debt.monto if debt.tipo_trx == 'Pre' else -debt.monto

            texto = "\n".join(f"{partner.name}: ${monto: ,.2f}" for partner, monto in resumen.items() if monto > 0)
            project.resumen_deuda_proveedores = texto
    
    #Calcular deuda total
    @api.depends('supplier_debt_ids')
    def _compute_supplier_debt(self):
        for project in self:
            total = 0.0
            for debt in project.supplier_debt_ids:
                if debt.tipo_trx == 'Pre':
                    total += debt.monto
                elif debt.tipo_trx == 'abn':
                    total -= debt.monto
            project.supplier_debt = total
        
            # Buscar la tarea "Gestionar Cartera"
            supplier_task = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('name', 'ilike', 'Gestionar Crédito Proveedores')
            ], limit=1)

            if supplier_task:
                supplier_task.supplier_debt = project.supplier_debt

    #Calcular el valor restante comisión
    @api.depends('commission_money', 'commission_debt_ids.abono')
    def _compute_commision_due(self):
        for project in self:
            total_paid = sum(project.commission_debt_ids.mapped('abono'))
            project.commission_due = project.commission_money - total_paid

            if project.commission_due <= 0 and project.dashboard_commission_id:
                project.dashboard_commission_id = False
            
            # Buscar la tarea "Gestionar Cartera"
            cartera_task = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('name', 'ilike', 'Gestionar Pago Comisiones')
            ], limit=1)

            if cartera_task:
                cartera_task.commission_due = project.commission_due

    #Abrir el wizard Cartera
    def action_open_payment_wizard(self):
        logger.info("Entra")
        self.ensure_one()
        return {
            'name': 'Registrar Pago',
            'type': 'ir.actions.act_window',
            'res_model': 'project.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
            },
        }

    #Abrir el wizard proveedores
    def action_open_supplier_debt_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar Transacción',
            'res_model': 'project.supplier.debt.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id
            }
        }  

    #Abrir el wizard comisiones
    def action_open_commission_debt_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Abonar a Comisión',
            'res_model': 'project.commission.debt.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'default_partner_id_v': self.partner_id_v.id
            }
        }  

    #Sobre escribe el método Create
    def create(self, vals_list):
        """Sobrescribe create para agregar las etapas en un orden específico."""
        stage_model = self.env['project.task.type']
        
        # Definir las etapas necesarias con su secuencia
        stage_names = ['Cotizar', 'Por Fabricar', 'Fabricando', 'Terminado','Proveedores' ,'Instalación', 'Entregado']
        stages = {}

        # Buscar o crear las etapas en el orden correcto
        for index, stage_name in enumerate(stage_names):
            stage = stage_model.search([('name', '=', stage_name)], limit=1)
            if not stage:
                stage = stage_model.create({
                    'name': stage_name,
                    'sequence': index  # Asegurar que se mantenga el orden correcto
                })
            else:
                # Si ya existe, aseguramos que la secuencia sea la correcta
                stage.write({'sequence': index}, cond = False)
            stages[stage_name] = stage


        projects = super().create(vals_list)

        for project in projects:
            # Asociar las etapas al proyecto
            for stage in stages.values():
                stage.write({'project_ids': [(4, project.id)]}, cond = False)

            # Crear la tarea "Cotizar" en la etapa "Cotizar"
            self.env['project.task'].create({
                'name': 'Cotizar',
                'project_id': project.id,
                'stage_id': stages['Cotizar'].id  # Asignar a la etapa "Cotizar"
            }, cond = False)
        
        return projects

    def _update_project_stage_info(self):
            stage_order = ['Cotizar', 'Por Fabricar', 'Fabricando', 'Terminado','Proveedores' ,'Instalación', 'Entregado']

            for project in self:
                tasks = project.task_ids.filtered(lambda t: t.stage_id.name in stage_order)
                tasks_min = project.task_ids.filtered(lambda t: t.stage_id.name in stage_order and t.stage_id.name != 'Cotizar')

                # Buscar la etapa más avanzada
                most_advanced_task = max(
                    tasks, key=lambda t: stage_order.index(t.stage_id.name)
                )
                stage_name = most_advanced_task.stage_id.name

                # Buscar la etapa menos avanzada (índice más bajo)
                try:
                    least_advanced_task = min(
                        tasks_min, key=lambda t: stage_order.index(t.stage_id.name)
                    )

                    least_stage_name = least_advanced_task.stage_id.name

                    logger.info("Mayor Estado"+stage_name)
                    logger.info("Menor Estado"+least_stage_name)

                except Exception as e:
                    pass

                status = ""
                #Color por defecto
                color = 9
                if stage_name == "Cotizar":
                    status = "Cotizando"
                    color = 8
                elif stage_name == "Por Fabricar":
                    status = "Por Fabricar"
                    color = 1                    
                elif stage_name == "Fabricando"  :
                    status = "Fabricando"
                    color = 3                           
                elif stage_name == "Terminado" and  least_stage_name != "Terminado" :
                    status = "Fabricando"
                    color = 3                        
                elif stage_name == "Terminado" and  least_stage_name == "Terminado" :
                    status = "Terminado"
                    color = 7 
                elif stage_name == "Proveedores" and  least_stage_name in ("Por Fabricar", "Fabricando", "Proveedores") :
                    status = "Fabricando"
                    color = 11                         
                elif stage_name == "Instalación" and  least_stage_name in ("Por Fabricar", "Fabricando", "Proveedores") :
                    status = "Instalando-Fabricando"
                    color = 11    
                elif stage_name == "Instalación" and  least_stage_name in ("Instalación", "Terminado") :
                    status = "Instalando"
                    color = 11    
                elif stage_name == "Entregado" and least_stage_name != "Entregado":
                    status = "Entregando"
                    color = 11    
                elif least_stage_name == "Entregado":
                    status = "Proyecto Entregado Completamente"
                    color = 10

                project.write({
                    'color': color,
                    'last_stage': status                })
       

    def action_project_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Registrar Pago',
            'res_model': 'project.payment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('CustomizeProject.view_project_payment_wizard_form').id,
            'target': 'new',
            'context': {
                'default_project_id': self.id,
            }
        }
    
    #Estado Final del Proyecto
    @api.depends('commission_due', 'supplier_debt', 'amount_due', 'last_stage')
    def _compute_estado_final(self):
        for record in self:
            if (
                record.commission_due == 0 and
                record.supplier_debt == 0 and
                record.amount_due == 0 and
                record.last_stage == "Proyecto Entregado Completamente"
            ):
                record.estado_final = "Finalizado"
            else:
                record.estado_final = ""