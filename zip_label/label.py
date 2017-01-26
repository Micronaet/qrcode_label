# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import os
import sys
import logging
import openerp
import qrcode
import urllib
import base64
import openerp.netsvc as netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, expression, orm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools import (DEFAULT_SERVER_DATE_FORMAT, 
    DEFAULT_SERVER_DATETIME_FORMAT, 
    DATETIME_FORMATS_MAP, 
    float_compare)


_logger = logging.getLogger(__name__)

class ZipLabel(orm.Model):
    """ Model name: ZipLabel
    """
        
    _name = 'zip.label'
    _description = 'Zip Label'
    _rec_name = 'code'
    _order = 'code'

    # -------------------------------------------------------------------------        
    # QR Code path block:
    # -------------------------------------------------------------------------        
    # TODO manage correctly:
    _qrcode_path = ['~', 'odoo', 'qrcode']
    _qrcode_ext = 'png'
    
    def get_qrcode_path(self):
        ''' Generate default path for qrcode image
        '''
        res = ''
        for folder in self._qrcode_path:
            res = os.path.join(res, folder)
        res = os.path.expanduser(res)
            
        try:    
            os.system('mkdir -p %s' % res)
            _logger.info('QRCode path folder: %s' % res) 
        except:
            _logger.error('Error generating path: %s' % res) 
        return res

    # -------------------------------------------------------------------------        
    # Override for generation QR Code:
    # -------------------------------------------------------------------------        
    def create(self, cr, uid, vals, context=None):
        """ Create a new record for a model ClassName
            @param cr: cursor to database
            @param uid: id of current user
            @param vals: provides a data for new record
            @param context: context arguments, like lang, time zone
            
            @return: returns a id of new record
        """
    
        res_id = super(ZipLabel, self).create(
            cr, uid, vals, context=context)
        # Generate QR Code    
        self.generate_qr_code(cr, uid, [res_id], context=context)
        return res_id
    
    def write(self, cr, uid, ids, vals, context=None):
        """ Update redord(s) comes in {ids}, with new value comes as {vals}
            return True on success, False otherwise
            @param cr: cursor to database
            @param uid: id of current user
            @param ids: list of record ids to be update
            @param vals: dict of new values to be set
            @param context: context arguments, like lang, time zone
            
            @return: True on success, False otherwise
        """    
        res = super(ZipLabel, self).write(
            cr, uid, ids, vals, context=context)

        # Generate QR Code    
        self.generate_qr_code(cr, uid, ids, context=context)
        return res
    
    
            
    # -------------------------------------------------------------------------        
    # Generation QR code
    # -------------------------------------------------------------------------        
    def generate_qr_code(self, cr, uid, ids, context=None):
        ''' Generate QR Code for label
        '''
        if type(ids) not in (list, tuple):
            ids = [ids]
        qr_mask = 'Zipperr\nCodice: [%s]\nIT: %s\nEN: %s'
        path = self.get_qrcode_path()
        
        for label in self.browse(cr, uid, ids, context=context):            
            item_id = label.id
            fullname = os.path.join(
                path, '%s.%s' % (item_id, self._qrcode_ext))
            
            qr_text = qr_mask % (
                label.code, 
                label.description_it, 
                label.description_en)    
            img = qrcode.make(qr_text)
            img.save(fullname)
        return True
    
    # -------------------------------------------------------------------------        
    # Fields function
    # -------------------------------------------------------------------------        
    def _get_qrcode_image(self, cr, uid, ids, field_name, arg, context=None):
        ''' Field function, for every ids test if there's image and return
            base64 format according to code value (images are jpg)
        '''
        res = {}
        
        # Parameter QR Code:
        path = self.get_qrcode_path()
        qr_ext = self._qrcode_ext
        
        for product in self.browse(cr, uid, ids, context=context):
            fullname = os.path.join(
                path, '%s.%s' % (product.id, qr_ext))
            try:
                (filename, header) = urllib.urlretrieve(fullname) 
                _logger.info('Read QR Code image: %s' % filename) 
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()
            except:
                img = ''
            res[product.id] = img
        return res
        
    _columns = {
        'code': fields.char(
            'Code', size=64, required=True),
        'description_it': fields.text('Description IT', required=True),
        'description_en': fields.text('Description EN', required=True),

        'qrcode': fields.function(
            _get_qrcode_image, type='binary', method=True),
        }
        
    _defaults = {
        # TODO code automatic
        }    
        
class SaleOrderLine(orm.Model):
    """ Model name: SaleOrderLine
    """
    
    _inherit = 'sale.order.line'
    
    def onchange_qrcode_box(self, cr, uid, ids, label_box, context=None):
        ''' QRcode box
        '''
        res = {'value': {'label_box': False}}
        
        res['value']['label_id'] = 3 # TODO 
        res['value']['name'] = 'Etichetta 1' # TODO 
        
        return res

    _columns = {
        'label_id': fields.many2one('zip.label', 'Label'),
        'label_box': fields.text('QRCode box'),
        }

# TODO remove:
class SaleOrder(orm.Model):
    """ Model name: SaleOrderLine
    """
    
    _inherit = 'sale.order'
    
    def onchange_qrcode_box(self, cr, uid, ids, label_box, context=None):
        ''' QRcode box
        '''
        res = {'value': {}}# {'label_box': False}}
        if not label_box:
            return res
        parts = label_box.split('[')[1:]
            
        codes = [] 
        for item in parts:
            codes.append(item.split(']')[0])
                
                        
        #res['value']['label_id'] = 3 # TODO 
        #res['value']['name'] = 'Etichetta 1' # TODO 
        res['value']['label_box'] = '%s' % (codes, )
        line_pool = self.pool.get('sale.order.line')
        label_pool = self.pool.get('zip.label')
        for code in codes:
            label_ids = label_pool.search(cr, uid, [
                ('code', '=', code)], context=context)
            if label_ids:
                label_id = label_ids[0]
            else:
                label_id = False        
            line_pool.create(cr, uid, {
                'order_id': ids[0],
                'name': code,
                'label_id': label_id,
                'product_uom_qty': 1.0,                
                }, context=context)           
        
        return res
        
    _columns = {
        'label_box': fields.text('QRCode box'),
        }
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
