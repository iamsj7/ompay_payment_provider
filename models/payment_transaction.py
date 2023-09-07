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
import json
import requests
from werkzeug import urls

from odoo import _, fields, models
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_acquirer_ompay.controllers.main import OMPayController
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    ompay_invoice_id = fields.Char('Invoice ID')

    def _retrieve_ompay_checkout_session(self):
        url = self.provider_id._get_ompay_urls()
        headers = self.provider_id._get_ompay_headers()
        ompay_merchant_key = self.provider_id.ompay_merchant_key  # Get the ompay_merchant_key
        res = requests.request("GET", url + f'/v1/merchants/{ompay_merchant_key}/hosted-payment/session/{self.provider_reference}', headers=headers)
        _logger.info(_("OMPay API OUTGOING URL: %s") % res)
        response = res.json()
        _logger.info(_("OMPay API OUTGOING URL: %s") % response)
        session_state = response.get('session_state')
        if session_state not in ['pending', 'used', 'expired', 'processing']:
            _logger.info(_("OMPay Error response session_state: %s") % response)
            raise ValidationError(_("OMPay is having some issues to confirm the payment, contact us for support!"))
        return response  # Return the complete response

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return OMPay-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'ompay':
            return res

        base_url = self.provider_id.get_base_url()
        if not self.partner_email:
            raise ValidationError(_("Email not set, please set the email and try again!"))

        """ customer_id = self.partner_id._create_ompay_customer(self.provider_id)
        """
        
        ompay_merchant_key = self.provider_id.ompay_merchant_key  # Get the ompay_merchant_key
        payload = {
            "intent": "sale",
            "payer": {
                "payment_type": "CC",
                "payer_info": {
                    "email": "iamsj7@gmail.com",
                    "billing_address": {
                        "line1": "test",
                        "city": "test",
                        "country_code": "OM",
                        "postal_code": "123",
                        "state": "muscat",
                        "phone": {
                            "number": "12345678"
                        }
                    }
                }
            },
            "transaction": {
                "amount": {
                    "currency": "OMR",
                    "total": float(self.amount)  # Convert to float if not already
                },
                "description": "purchase",
                "invoice_number": self.provider_reference,  # Use the provider reference or another suitable identifier
                "return_url": urls.url_join(base_url, OMPayController._success_url + '?reference=%s' % self.reference),
                "cancel_url": "https://ompay.com/cancel",
                "items": [{
                    "sku": "30065",
                    "name": "Test product",
                    "quantity": 1,
                    "price": float(self.amount),  # Convert to float if not already
                    "shipping": 0,
                    "currency": "OMR"
                }]
            }
        }

        url = self.provider_id._get_ompay_urls()
        headers = self.provider_id._get_ompay_headers()
        res = requests.request("POST", f"{url}/v1/merchants/{ompay_merchant_key}/hosted-payment", headers=headers, data=json.dumps(payload))
        response = res.json()

        if 'invoice_number' in response and 'hosted_page_link' in response:
            invoice_number = response.get('invoice_number')
            hosted_page_link = response.get('hosted_page_link')

            # Update the api_url with the hosted_page_link
            payload.update({'api_url': hosted_page_link})
        else:
            _logger.info(_("OMPAY Error response: %s") % response)
            raise ValidationError(_("OMPAY is having some issues, contact us for support!"))

        _logger.info(_("OMPay BEFORE SESSION ID: %s" % response))
        session_id = response['session_id']
        self.sudo().write({'provider_reference': session_id})
        _logger.info("Provider Reference: %s" % self.provider_reference)
        api_url = f'{url}/v1/merchants/{ompay_merchant_key}/hosted-payment/page/{session_id}'
        payload.update({'api_url': '/payment/ompay/redirect?redirect_url=%s' % base64.urlsafe_b64encode(api_url.encode('utf-8')).decode('utf-8')})
        return payload

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on OMPay data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'ompay' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference')
        if not reference:
            raise ValidationError(
                "OMPay: " + _(
                    "Received data with missing reference %(r)s.",
                    r=reference
                )
            )

        tx = self.search([('reference', '=', reference), ('provider_code', '=', provider_code)])
        if not tx:
            raise ValidationError(
                "OMPay: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_notification_data(self, notification_data):
        """ Override to process the transaction based on OMPAY data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data are received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'ompay':
            return

        response = self._retrieve_ompay_checkout_session()

        session_state = response.get('session_state')
        self.write({
            'ompay_invoice_id': response.get('session_state') or '',
        })

        if session_state == 'used':
            _logger.info('OMPAY payment for tx %s: set as DONE' % (self.reference))
            self._set_done()
        elif session_state == 'pending':
            _logger.info('OMPAY payment for tx %s: set as PENDING' % (self.reference))
            self._set_pending()
        elif session_state == 'expired':
            _logger.info('OMPAY payment for tx %s: set as CANCELLED' % (self.reference))
            self._set_canceled()
        else:
            msg = 'Received unrecognized response for OMPAY Payment %s, set as error' % (self.reference)
            _logger.info(msg)
            self.write({
                'state_message': msg
            })
            self._set_error(msg)
