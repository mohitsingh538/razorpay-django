from django.shortcuts import render
import datetime
import razorpay
import sweetify
import hmac
import hashlib
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from .models import Transaction, Razorpay_data

# Create your views here.


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

@login_required
def payment(request):
    if request.method == 'GET':
        invoice = request.GET.get('invoice', None)
        if invoice:
            fetch_invoice = Transaction.objects.get(invoice_id=invoice)

            if not fetch_invoice.razorpay_data.rzp_order_id:
                order_amount = fetch_invoice.amount * 100  # Since Razorpay accepts amount format in Paise,
                # so Rs.500 should be 50000

                # CREATING ORDER
                response = client.order.create(
                    dict(amount=order_amount, currency='INR', receipt=invoice,
                         payment_capture='0'))
                order_status = response['status']

                if order_status == 'created':
                    order = Razorpay_data.objects.create(rzp_order_id=response['id'])
                    fetch_invoice.razorpay_data = order.id
                    fetch_invoice.save()

            if fetch_invoice.razorpay_data.status:
                context = {'invoice_details': fetch_invoice}

            else:
                context = {'invoice_details': fetch_invoice, 'key_id': settings.RAZORPAY_KEY_ID}

            return render(request, 'integration/templates/payment-details.html', context)

        else:
            return redirect('my_payments')  # Or do something else

    else:
        return redirect('access-denied')    # Or do something else


@login_required
def payment_status(request):
    if request.method == 'POST':
        response = request.POST
        invoice = request.GET.get('invoice', None)

        # VERIFYING SIGNATURE
        c_key = bytes(settings.RAZORPAY_SECRET_KEY, 'utf8')
        c_msg = bytes(f"{response['razorpay_order_id']}|{response['razorpay_payment_id']}", 'utf8')

        h = hmac.new(c_key, c_msg, hashlib.sha256).hexdigest()

        if h == response['razorpay_signature']:

            data_get = Razorpay_data.objects.filter(rzp_order_id=response['razorpay_order_id'])

            #   CAPTURING PAYMENT

            amount = (client.payment.fetch(response['razorpay_payment_id']))['amount']
            capture = client.payment.capture(response['razorpay_payment_id'], amount)

            if capture['status'] == 'captured' and capture['captured'] is True:
                data_get.update(status=True, rzp_payment_id=capture['id'], method=capture['method'],
                                paid_on=datetime.datetime.now(), payment_email=capture['email'], payment_contact=capture['contact'])

                sweetify.success(request, title='Payment Success!', icon='success',
                                 text=f"Your payment of Rs.{(capture['amount']) // 100} has been received.", timer=5000,
                                 button='Ok', customClass={'confirmButton': 'btn btn-danger'}, buttonsStyling=False)

            else:
                messages.error(request, capture['error_description'])

        else:
            messages.error(request, "Oops...Signature verification failed!")

        return HttpResponseRedirect(f'/razorpay/?invoice={invoice}')

    else:
        return redirect('access-denied')
