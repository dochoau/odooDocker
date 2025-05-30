{
    'name': "CustomizeProject",
    'version': '1.0',
    'summary': "Modifica los proyectos y las cotizaciones",
    'category': 'Project',
    'author': "David Ochoa",
    'depends': ['project', 'sale','mrp', 'CustomizeClient','CustomizeSaleOrder'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/kanban_view.xml',
        'views/kanban_project_view.xml',
        'views/cartera_view.xml',
        'views/cartera_list_view.xml',
        'views/supplier_debt_view.xml',
        'views/project_dashboard_debt_view.xml',
        'views/commission_debt_view.xml',
        'views/project_dashboard_commission_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True
}