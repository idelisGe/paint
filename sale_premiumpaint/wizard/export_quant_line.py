# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import contextlib
import io

from odoo import api, fields, models, tools, _
from odoo.tools.misc import xlwt

class QuantValuationExport(models.TransientModel):
    _name = "quant.valuation.export"

    name = fields.Char('File Name', readonly=True)
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')

    @api.multi
    def _get_headers(self):
        return [
            'Producto',
            'Tienda',
            'Cantidad',
            'Valor',
        ]
    
    @api.multi
    def act_getfile(self):
        this = self[0]
        domain = [('product_id.type', '=', 'product'),('location_id.usage', '=', 'internal')]
        quant_data = self.env['stock.quant'].read_group(domain,fields=['product_id','location_id','quantity'], groupby=['product_id','location_id'])
        locations = self.env['stock.location'].search([('usage', '=', 'internal')])
        print (locations)
        location_qty = {'product_id': '', 'quantity': 0.0, 'inventory_value': 0.0}
        location_header = {}
        for location in locations:
            warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', location.id)], limit=1)
            location_qty.setdefault(location.id, 0.0)
            location_header.setdefault(location.id, warehouse.name if warehouse else location.name)
        quant_result = []
        for qd in quant_data:
            product = self.env['product.product'].browse(qd['product_id'][0])
            quant_item = location_qty.copy()
            quant_item.update({'product_id': qd['product_id'][1], 'quantity': qd['quantity'], 'inventory_value': product.stock_value})
            if '__domain' in qd:
                quant_item.update({'product_id': qd['product_id'][1], 'inventory_value': product.stock_value})
                quant_location = self.env['stock.quant'].read_group(qd['__domain'],fields=['location_id','quantity'], groupby=['location_id'])
                for ql in quant_location:
                    quant_item.update({ql['location_id'][0]: ql['quantity']})
            quant_result.append(quant_item)
        with contextlib.closing(io.BytesIO()) as buf:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Reporte Valoración Inventario')
            header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")

            worksheet.write(0,0,'Producto',header_bold)
            key_locations = []
            col = 1
            for key,value in location_header.items():
                worksheet.write(0,col,value,header_bold)
                key_locations.append(key)
                col += 1
            worksheet.write(0,col,'Cantidad Total',header_bold)
            worksheet.write(0,col + 1,'Valor',header_bold)

            row = 1
            for qr in quant_result:
                cell_num = xlwt.easyxf(num_format_str="#,##0.00")
                worksheet.write(row,0,qr['product_id'])
                col = 1
                for key_location in key_locations:
                    worksheet.write(row,col,qr[key_location],cell_num)
                    col += 1
                worksheet.write(row,col,qr['quantity'],cell_num)
                worksheet.write(row,col + 1,qr['inventory_value'],cell_num)
                row += 1

            workbook.save(buf)
            out = base64.encodestring(buf.getvalue())

        filename = 'Reporte valor de Inventario'
        extension = 'xls'
        name = "%s.%s" % (filename, extension)
        this.write({'state': 'get', 'data': out, 'name': name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'quant.valuation.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
