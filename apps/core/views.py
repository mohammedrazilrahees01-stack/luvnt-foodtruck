# apps/core/views.py
from django.shortcuts import render

def frontend(request):
    # optionalcontext: pass razorpay key if you want JS to read it
    return render(request, 'frontend.html', {
        # 'RAZORPAY_KEY_ID': os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_dummy')
    })
