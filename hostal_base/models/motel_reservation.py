from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class MotelReservation(models.Model):
    _name = "motel.reservation"
    _description = 'Motel Reservation'

    name = fields.Char(required=True)
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    room_id = fields.Many2one(comodel_name="motel.room", required=True)
    motel_id = fields.Many2one(comodel_name="motel.motel",
                               related='room_id.motel_id',
                               store=True,
                               readonly=True)
    checkin_date = fields.Date()
    checkout_date = fields.Date()
    nights = fields.Integer(readonly=True, compute= '_compute_nights')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirmed', 'Confirmed'),
         ('checked_in', 'Checked In'),
         ('checked_out', 'Checked Out'),
         ('cancelled', 'Cancelled')]
    )
    pet = fields.Boolean()
    help_pet = fields.Boolean(string="Service Animal")
    has_room_service = fields.Boolean(string="Room Service")
    room_service_fee = fields.Float(default=25)
    restaurant_order_ids = fields.One2many(
        comodel_name='motel.restaurant.order',
        inverse_name='reservation_id',
        string="Restaurant Orders"
    )
    has_wifi_service = fields.Boolean(string="Wifi")
    is_frequent = fields.Boolean(
        string="Frequent Client",
        compute="_compute_is_frequent",
        store= True
    )
    total_price = fields.Float(
        readonly=True,
        store=True,
        compute="_compute_total_price")

    @api.constrains('room_id', 'checkin_date', 'checkout_date')
    def _check_room_id(self):
        for res in self:
            if not res.checkin_date or not res.checkout_date:
                continue

            reservas_solapadas = self.env["motel.reservation"].search([
                ('room_id','=',res.room_id),
                 ('id','!=',res.id),
                 ('checkin_date','<',res.checkout_date),
                 ('checkout_date','>',res.checkin_date),
                 ('state','!=','cancelled')]
            )

            if reservas_solapadas:
                raise UserError("This room is already booked for these dates.")

    @api.constrains('checkin_date', 'checkout_date')
    def _check_validation(self):
        for res in self:
            if res.checkin_date and res.checkout_date and res.checkin_date >= res.checkout_date:
                raise ValidationError("Incorrect information during check-in or check-out.")

    @api.depends('checkin_date', 'checkout_date')
    def _compute_nights(self):
        for res in self:
            if res.checkin_date and res.checkout_date:
                res.nights = (res.checkout_date - res.checkin_date).days
            else:
                res.nights = 0

    @api.constrains('room_id')
    def _check_available_room(self):
        for res in self:
            if not res.room_id.active:
                raise UserError("This room is not available.")

    @api.depends('partner_id', 'checkout_date', 'state')
    def _compute_is_frequent(self):
        hoy= fields.Date.today()
        hace_5_anos = fields.Date.subtract(hoy, years=5)

        for res in self:
            reservas = self.env['motel.reservation'].search([
                ('partner_id','=',res.partner_id.id),
                ('checkout_date','>=',hace_5_anos),
                ('checkout_date','<=',hoy),
                ('state','!=','cancelled')
            ])

            res.is_frequent = len(reservas) > 10

    @api.depends('nights',
                 'room_id.room_type',
                 'has_room_service',
                 'pet',
                 'help_pet',
                 'has_wifi_service',
                 'is_frequent',
    )
    def _compute_total_price(self):
        for res in self:
            sum_total_price = 0.0

            if res.room_id.room_type == 'normal':
                room_price=100
            elif res.room_id.room_type == 'premium':
                room_price = 200
            else:
                room_price = 0

            if res.is_frequent:
                sum_total_price *= 0.75

            if res.nights > 5:
                sum_total_price += 5 * room_price + (res.nights - 5) * room_price * 1.5
            else:
                sum_total_price += res.nights * room_price

            if res.has_room_service:
                sum_total_price += 25

            if res.pet:
                if not res.help_pet:
                    valor = 25
                else:
                    valor = 0

                sum_total_price+= valor

            if res.has_wifi_service:
                sum_total_price += res.nights * 2



            if res.partner_id:
                res.total_price = sum_total_price