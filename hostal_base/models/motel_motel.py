from odoo import models, fields, api

class MotelMotel(models.Model):
    _name = "motel.motel"
    _description = "Motel"

    name = fields.Char(required=True)
    company_id = fields.Many2one(comodel_name='res.company', required=True)
    latitude = fields.Float()
    longitude = fields.Float()
    parking_slots = fields.Integer(default=20)
    wifi_price = fields.Float(default=2)
    active = fields.Boolean(default=True)