# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode, b64encode
from odoo import api, fields, models


class account_payment_subtype(models.Model):
    _name = "account.payment.subtype"
    _description = "Payment Subtype"

    name = fields.Char(required=True, translate=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])


class account_payment(models.Model):
    _inherit = "account.payment"

    payment_subtype_id = fields.Many2one('account.payment.subtype', string='Payment Subtype')
    #Es necesario?
    warehouse_id = fields.Many2one(related='create_uid.sale_team_id.warehouse_id', string="Almacen", store=True, readonly=True)

    @api.onchange('payment_subtype_id')
    def _onchange_payment_subtype(self):
        if self.payment_subtype_id:
            self.journal_id = self.payment_subtype_id.journal_id
        else:
            self.journal_id = False
