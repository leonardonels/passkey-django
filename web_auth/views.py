from django.shortcuts import render, get_object_or_404, redirect
from users.models import User
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import AttestationConveyancePreference, RegistrationCredential
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json
from mysite.settings import REPLYING_PARTY_ID, REPLYING_PARY_NAME, ORIGIN
from django.http import JsonResponse
import json, secrets
from rest_framework.views import APIView
from .models import Credential
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def registration(request):

    #get User informations
    user=request.user

    #start the ceremony
    options=generate_registration_options(
        rp_id=REPLYING_PARTY_ID,
        rp_name=REPLYING_PARY_NAME,
        user_id=str(user.id).encode('utf-8'),
        user_name=user.username,
        attestation=AttestationConveyancePreference.DIRECT,
        #temporarly no auth verification required
    )

    #create and save the challenge
    challenge=options.challenge
    cache.set(f'challenge_{user.id}', challenge, timeout=300)

    return JsonResponse(json.loads(options_to_json(options)))
    
def registration_verification(request):

    #get User informations
    user=request.user

    #start registration flow
    request_body=request.body.decode('utf-8')
    print(request_body)
    request_data = json.loads(request_body)

    try:
        id=request_data.get('id')
        raw_id = request_data.get('rawId')
        response = request_data.get('response')

        print(type(id))
        print(type(raw_id))
        print(type(response))

        credential=parse_registration_credential_json(request_body)
        verification=verify_registration_response(
            credential=credential,
            expected_challenge=cache.get(f'challenge_{user.id}'),
            expected_rp_id=REPLYING_PARTY_ID,
            expected_origin=ORIGIN,
        )
    except Exception as err:
        return JsonResponse({"verified":False, "msg":str(err), "status":400})
        
    #creating a new credential for the user
    new_credential = Credential.objects.create(
        user=user,
        credential_id=verification.credential_id,
        public_key=verification.credential_public_key,
        sign_counts=verification.sign_count,
        transports=credential.response.transports
    )

    return JsonResponse({"verified":True})

def remove_passkey(request):
    Credential.objects.filter(user=request.user).delete()
    return redirect('/users/profile')