from odoo import models, fields, api

class MotelRoom(models.Model):
    _name = "motel.room"
    _description = 'Motel Room'

    name = fields.Char()
    room_number = fields.Integer()
    motel_id = fields.Many2one(
        comodel_name='motel.motel'
    )
    room_type = fields.Selection(
        [('normal','Normal'),
         ('premium', 'Premium')]
    )
    floor = fields.Integer()
    price = fields.Float()
    active = fields.Boolean(default= True)
