# Razorpay - Django Secure Integration

<img src="https://upload.wikimedia.org/wikipedia/en/8/89/Razorpay_logo.svg" width="200px">



# Introduction

The [documentation](https://razorpay.com/docs/payment-gateway/server-integration/python/) provided by Razorpay for Python is not detailed, and somewhat confusing for newbies. Moreover, the default [package](https://pypi.org/project/razorpay/) has some bugs. Most likely, you'd end up getting 'None' response while verifying payment signature if you are using the official razorpay package.

My Django app is based on the default package with some tweaks that I'd be explaining later.

# Requirements
- `razorpay`
- `sweetify`    (optional)

# Install
```bash
pip install -r requirements.txt
```
Make following changes in `settings.py` file
```bash
if DEBUG:
    RAZORPAY_KEY_ID = ''    #Enter your Razorpay test KEY ID
    RAZORPAY_SECRET_KEY = ''    #Enter your Razorpay test KEY SECRET
else:
    RAZORPAY_KEY_ID = '' #Enter your Razorpay live KEY ID
    RAZORPAY_SECRET_KEY = ''    #Enter your Razorpay live KEY SECRET
```

If you wish to run this app as it is, run:
```bash
python manage.py makemigrations
python manage.py migrate
```
Please note that user registration & login system is missing in this app because I have built it for integration purpose, so your requirements could be different than mine.

**1.** We first need to create an invoice ID and amount in the DB which will be linked to a certain user (please check `models.py` for more info). I have used uuid for generating invoice ID.
```bash
invoice_id = uuid.uuid4()
amount = 500
user = customer.id      # or anything you want
```
**2.** Generating Razorpay order ID (Please refer to `views.py` file for details)
```bash
fetch_invoice = Transaction.objects.get(invoice_id=invoice)
order_amount = fetch_invoice.amount * 100       # amount should be in Paise

# CREATING ORDER
response = client.order.create(dict(amount=order_amount, 
currency='INR', receipt=invoice, payment_capture='0'))

order_status = response['status']
    if order_status == 'created':
        order = Razorpay_data.objects.create(rzp_order_id=response['id'])
        fetch_invoice.razorpay_data = order.id
        fetch_invoice.save()
```

**3.** Pass the required information in Razorpay form on your payment page (refer to `integration/templates/invoice.html`)
```bash
<a onclick="$('form#razorpay_payment').submit();">
    <button class="btn btn-info" type="button">
        <i class="fa fa-credit-card"></i> Pay Now
    </button>
</a>

<form action="{% url 'payment_status' %}?invoice={{ invoice_details.invoice_id }}" method="POST" name="razorpay_payment" id="razorpay_payment">
    {% csrf_token %}
    <script src="https://checkout.razorpay.com/v1/checkout.js"
        data-key="{{ key_id }}"
        data-amount="{{ invoice_details.amount }}"
        data-currency="INR"
        data-order_id="{{ invoice_details.razorpay_data.rzp_order_id }}"
        data-name="YOUR COMPANY NAME"
        data-description="PRODUCT/SERVICE DESCRIPTION HERE"
        data-image="link-to-your-logo-here"
        data-prefill.name="{{ user.full_name }}"
        data-prefill.email="{{ user.email }}"
        data-theme.color="#7b68ee">
    </script>
</form>
```

**4.** If everything is integrated properly, you would see this pop-up on clicking the Pay Now button

![Successfully integrated](https://github.com/ohlc-ai/razorpay-django/blob/master/static/payments.png?raw=true)

**5.** If payment is authorised, Razorpay would send `razorpay_payment_id`, `razorpay_order_id` and `razorpay_signature` response via POST:

```bash
response = request.POST

# VERIFYING SIGNATURE
c_key = bytes(settings.RAZORPAY_SECRET_KEY, 'utf8')
c_msg = bytes(f"{response['razorpay_order_id']}|{response['razorpay_payment_id']}", 'utf8')

h = hmac.new(c_key, c_msg, hashlib.sha256).hexdigest()

if h == response['razorpay_signature']:

    amount = (client.payment.fetch(response['razorpay_payment_id']))['amount']     # Getting amount for capturing payment
    capture = client.payment.capture(response['razorpay_payment_id'], amount)     # Capturing payment

    if capture['status'] == 'captured' and capture['captured'] is True:
        # Do something ...
```

### Contact

**Issues should be raised directly in the repository.** For additional questions or comments please email me at mohit@terrebrown.com
