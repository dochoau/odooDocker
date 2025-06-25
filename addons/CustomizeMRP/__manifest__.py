{
    "name": "CustomizeMRP",
    "version": "1.2",
    "depends": ["sale", "mrp", "project"],
    'license': 'LGPL-3',
    'author': "David Ochoa",
    "installable": True,
    "auto_install": False,
    'data': [
        'security/ir.model.access.csv',
        'views/custom_mrp_view.xml',
        'views/custom_mrp_list.xml',
        'views/product_file_views.xml'
    ],
}