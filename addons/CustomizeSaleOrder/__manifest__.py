{
    "name": "CustomizeSaleOrder",
    "version": "1.0",
    "depends": ["sale", "mrp", "hr", "project","CustomizeMRP"],
    'license': 'LGPL-3',
    'author': "David Ochoa",
    "data": [
        "views/cotizacion_view.xml",
        "reports/report_saleorder_template.xml",
        "reports/reports_f.xml",
     ],
    "installable": True,
    "auto_install": False,
}