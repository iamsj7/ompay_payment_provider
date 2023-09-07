-- disable ompay payment provider
UPDATE payment_provider
   SET ompay_public_key = NULL,
       ompay_secret_key = NULL,
       ompay_merchant_key = NULL;