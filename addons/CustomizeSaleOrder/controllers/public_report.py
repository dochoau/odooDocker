from odoo import http
from odoo.http import request

class PublicReportController(http.Controller):

    @http.route(['/cotizacion/publica/<int:order_id>', '/es/cotizacion/publica/<int:order_id>'], type='http', auth='public')
    def public_quotation(self, order_id):
        sale_order = request.env['sale.order'].sudo().browse(order_id)
        if not sale_order.exists():
            return request.not_found()

        html = request.env['ir.ui.view']._render_template(
            'CustomizeSaleOrder.report_saleorder_custom_html_nopdf',
            {'docs': sale_order}
        )

        return request.make_response(html, headers=[
            ('Content-Type', 'text/html'),
        ])
    
