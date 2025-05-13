from . import models

from odoo import api, SUPERUSER_ID
import json
def funcion_hook(env):
    print("Si entró aquí")
# Crear un nuevo tipo de identificación
    env['l10n_latam.identification.type'].with_context(lang='es_CO').create([
            {
                'sequence': 120,
                'name': "CC",  #
                'active': True,
                'is_vat': False
            },
            {
                'sequence': 130,
                'name': "NIT",
                'active': True,
                'is_vat': False
            }
        ])

