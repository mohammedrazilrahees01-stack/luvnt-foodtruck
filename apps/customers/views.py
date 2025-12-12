# apps/customers/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from .models import Customer

# initialize once (e.g. in this module import). adapt path to your service account json
if not firebase_admin._apps:
    cred = credentials.Certificate("config/firebase-admin.json")
    firebase_admin.initialize_app(cred)

@csrf_exempt
def firebase_login(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = json.loads(request.body.decode("utf-8"))
    id_token = payload.get("id_token")
    if not id_token:
        return JsonResponse({"detail": "id_token required"}, status=400)
    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception as e:
        return JsonResponse({"detail": "Invalid token", "error": str(e)}, status=400)

    # decoded has fields like uid, email, name, phone_number
    uid = decoded.get("uid")
    email = decoded.get("email")
    phone = decoded.get("phone_number")
    name = decoded.get("name") or decoded.get("display_name") or ""

    # create or get Customer
    customer, created = Customer.objects.get_or_create(
        firebase_uid=uid,
        defaults={"name": name, "email": email or "", "phone": phone or ""}
    )
    # if the model doesn't have firebase_uid field, use email or phone for lookup.
    # ensure your Customer model has fields: firebase_uid (CharField, unique, nullable), name, email, phone

    # Optionally, create a Django session for this user (if you prefer server sessions)
    # from django.contrib.auth import login, get_user_model
    # ... custom user handling if you have auth user model

    # Return profile data
    return JsonResponse({
        "id": customer.id,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
    })
