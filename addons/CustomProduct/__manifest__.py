{
    'name': 'CustomProduct',
    'version': '1.0',
    'summary': 'Catálogo de imágenes para productos',
        'license': 'LGPL-3', 
    'author': 'David Ochoa',
    'category': 'Product',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/product_image_catalog_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}