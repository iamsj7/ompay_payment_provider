# ******************************************************************************
# Copyright (c) [2023] [Shaik Jaleel]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# For more information, please refer to https://github.com/iamsj7/ompay_payment_provider.
# ******************************************************************************

import base64
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class OMPayController(http.Controller):
    _success_url = '/payment/ompay/success'
    _cancel_url = '/payment/ompay/cancel'

    @http.route([_success_url, _cancel_url], type='http', auth='public', csrf=False, save_session=False)
    def ompay_handle_feedback(self, **response):
        _logger.info('OMPAY: entering form_feedback with post response %s', pprint.pformat(response))

        # Extract the 'session_state' from the response
        session_state = response.get('session_state')
        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
            'ompay', response
        )
        tx_sudo._handle_notification_data('ompay', response)
        return request.redirect('/payment/status')

    @http.route('/payment/ompay/redirect', type='http', auth='public', csrf=False, save_session=False)
    def ompay_redirect(self, **post):
        redirect_url = base64.urlsafe_b64decode(post.get('redirect_url').encode('utf-8')).decode('utf-8')
        return werkzeug.utils.redirect(redirect_url)
