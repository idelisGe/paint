# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.price_total')
    def _compute_calculate_cost(self):
        """
        Compute the total cost of the SO.
        """
        for order in self:
            amount_calculate_cost = 0.0
            for line in order.order_line:
                amount_calculate_cost += (line.product_id.standard_price * line.product_uom_qty)
            order.update({
                'amount_calculate_cost': amount_calculate_cost
            })

    @api.depends('payment_term_id')
    def _compute_payment_type(self):
        for sale in self:
            sale_pt_id = sale.payment_term_id.id if sale.payment_term_id else False
            immediate_pt = self.env.ref('account.account_payment_term_immediate')
            immediate_pt_id = immediate_pt.id if immediate_pt else False
            sale.payment_type = 'Contado' if sale_pt_id in (immediate_pt_id, False) else 'Credito'

    @api.model
    def _default_warehouse_id(self):
        team = self.env['crm.team']._get_default_team_id()
        warehouse_ids = super(SaleOrder, self)._default_warehouse_id()
        return team.warehouse_id if (team and team.warehouse_id) else warehouse_ids

    payment_type = fields.Char(
        'Es Credito', compute='_compute_payment_type', store=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id)
    amount_calculate_cost = fields.Monetary(string='Costo', store=True, readonly=True, compute='_compute_calculate_cost')


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        print ("_create_invoice")
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        invoice.write({'payment_type': order.payment_type})
        return invoice
 