from odoo import models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def get_image_webp(self, partner_id):
        """Retorna la imagen del cliente en base64 (formato webp)."""
        partner = self.browse(partner_id)
        if partner.exists() and partner.image_1920:
            try:
                return partner.image_1920.decode('utf-8')
            except Exception:
                return ''
        return ''
