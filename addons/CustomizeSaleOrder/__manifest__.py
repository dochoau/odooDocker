{
    "name": "CustomizeSaleOrder",
    "version": "1.0",
    "depends": ["sale", "mrp", "hr", "project","CustomizeMRP"],
    'license': 'LGPL-3',
    'author': "David Ochoa",
    "data": [
        "views/cotizacion_view.xml",
        "views/confirm_wizard.xml",
        "reports/report_saleorder_template.xml",
        "reports/reports_f.xml",
        "reports/report_sale_order_html.xml",
        'security/ir.model.access.csv',
     ],
    "installable": True,
    "auto_install": False,
}