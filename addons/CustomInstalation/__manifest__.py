{
    "name": "CustomizeInstalation",
    "version": "1.0",
    "depends": ["project"],
    'license': 'LGPL-3',
    'author': "David Ochoa",
    "installable": True,
    "auto_install": False,
    'data': [
        'security/ir.model.access.csv',
        'views/custom_instalation.xml',
        'views/confirmation_instalation.xml'
    ],
}