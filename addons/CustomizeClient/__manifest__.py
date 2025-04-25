{
    'name': 'Customizeclient',
    'version': '1.0',
    'author': 'David',
    'license': 'LGPL-3',  # Agrega esta línea
    'category': 'Localization',
    'summary': 'Agrega tipos de identificación colombianos (CC y NIT)',
    'depends': ['base','l10n_latam_base'],

    'installable': True,
    'application': False,
    'auto_install': True,
    'post_init_hook': 'funcion_hook',
}