# -*- coding: utf-8 -*-

from odoo import api, models, fields


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.multi
    def _compute_inventory_value(self):
        for quant in self:
            if quant.company_id != self.env.user.company_id:
                # if the company of the quant is different than the current user company, force the company in the context
                # then re-do a browse to read the property fields for the good company.
                quant = quant.with_context(force_company=quant.company_id.id)
            quant.inventory_value = quant.product_id.stock_value

    inventory_value = fields.Float('Inventory Value', compute='_compute_inventory_value', readonly=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        " Overwrite the read_group in order to sum the function field 'inventory_value' in group by "
        # TDE NOTE: WHAAAAT ??? is this because inventory_value is not stored ?
        # TDE FIXME: why not storing the inventory_value field ? company_id is required, stored, and should not create issues
        res = super(StockQuant, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'inventory_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    inv_value = 0.0
                    for line2 in lines:
                        inv_value += line2.inventory_value
                    line['inventory_value'] = inv_value
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
