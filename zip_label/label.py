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
    
    # TODO manage correctly:
    _qrcode_path = '~/photo/db_name/quotation'
    
    def generate_qr_code(self, cr, uid, ids, context=None):
        ''' Generate QR Code for label
        '''
        for label in self.browse(cr, uid, ids, context=context):
            path = self._qrcode_path
            
            item_id = label.id
            fullname = os.path.join(path, '%s.png' % item_id)
            
            code = label.code
            text_it = label.description_it
            text_en = label.description_en
            qr_mask = 'Zipperr\nCodice: %s\IT: %s\nEN: %s'
            qr_text = qr_mask % (code, text_it, text_en)    
            img = qrcode.make(qr_text)
            img.save(fullname)
        return True
    
    def get_quotation_image(self, cr, uid, item, context=None):
        ''' Get single image for the file
            (default path is ~/photo/db_name/quotation
        '''        
        img = ''         
        extension = "jpg"
        path = os.path.expanduser(self._qrcode_path)

        product_browse=self.browse(cr, uid, item, context=context)
        # Image compoesed with code format (code.jpg)
        if product_browse.default_code:
            try:
                (filename, header) = urllib.urlretrieve("%s/%s.%s"%(image_path, product_browse.default_code.replace(" ", "_"), extension)) # code image
                f = open(filename , 'rb')
                img = base64.encodestring(f.read())
                f.close()
            except:
                img = ''
            
            if not img: # empty image:
                try:
                    (filename, header) = urllib.urlretrieve(empty_image) # empty setted up on folder
                    f = open(filename , 'rb')
                    img = base64.encodestring(f.read())
                    f.close()
                except:
                    img = ''
        return img

    # Fields function:
    def _get_quotation_image(self, cr, uid, ids, field_name, arg, context=None):
        ''' Field function, for every ids test if there's image and return
            base64 format according to code value (images are jpg)
        '''
        res = {}
        for item in ids:
            res[item] = self.get_quotation_image(cr, uid, item, context=context)
        return res    
            _columns = {
        'code': fields.char(
            'Code', size=64, required=True),
        'description_it': fields.text('Description IT', required=True)
        'description_en': fields.text('Description EN', required=True)
        # qrcode function binary
        'qrcode': fields.function(
            _get_qrcode_image, type="binary", method=True),
        }
        
    _defaults = {
        # TODO code automatic
        }    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
