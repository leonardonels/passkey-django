from django.shortcuts import render, get_object_or_404, redirect
from users.models import User
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import AttestationConveyancePreference, UserVerificationRequirement, PublicKeyCredentialDescriptor, PublicKeyCredentialType
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json
from webauthn.helpers.parse_authentication_credential_json import parse_authentication_credential_json
from mysite.settings import REPLYING_PARTY_ID, REPLYING_PARY_NAME, ORIGIN
from django.http import JsonResponse
import json, secrets, struct, base64
from rest_framework.views import APIView
from .models import Credential
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from typing import List


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
    try:
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
    )
    new_credential.set_transports(credential.response.transports)

    return JsonResponse({"verified":True})


def authentication(request):
    username = request.session['username']
    user=get_object_or_404(User, username=username)
    allow_credentials: List[PublicKeyCredentialDescriptor] = []

    for cred in user.credentials.all():
        allow_credentials.append(
            PublicKeyCredentialDescriptor(
                id=cred.id_bytes,
                type=PublicKeyCredentialType.PUBLIC_KEY,
                transports=cred.get_transports()
            )
        )

    options=generate_authentication_options(
        rp_id=REPLYING_PARTY_ID,
        allow_credentials=allow_credentials,
    )

    #create and save the challenge
    challenge=options.challenge
    cache.set(f'challenge', challenge, timeout=300)
    print(cache.get(f'challenge_{user.id}'))

    return JsonResponse(json.loads(options_to_json(options)))


def authentication_verification(request):
    request_body=request.body.decode('utf-8')
    data = json.loads(request_body)
    username = data.get('username', None)
    user=get_object_or_404(User, username=username)

    #print(cache.get(f'challenge_{user.id}'))
    
    try:
        request_credential=parse_authentication_credential_json(request_body)
        user_credential = Credential.objects.filter(user_id=user.id, id=request_credential.raw_id).first()
        print(user_credential)

        if not user_credential:
            raise Exception("User does not have credentials with give ID")
        
        verification=verify_authentication_response(
            Credential=request_credential,
            expected_challenge=cache.get(f'challenge_{user.id}'),
            expected_rp_id=REPLYING_PARTY_ID,
            expected_origin=ORIGIN,
            credential_public_key=user_credential.public_key,
            credential_current_sign_count=user_credential.sign_counts,
            require_user_verification=True,
        )
    except Exception as err:
        return JsonResponse({"verified":False, "msg":str(err), "status":400})
    
    user_credential.sign_counts=verification.new_sign_count
    return JsonResponse({"verified":True})



def remove_passkey(request):
    Credential.objects.filter(user=request.user).delete()
    return redirect('/users/profile')


def login_with_passkey(request):
    return render(request, 'login_with_passkey.html')

def set_username_in_session(request):
    if request.method == 'POST':
        request_data=json.loads(request.body)
        username = request_data.get('username')
        if username:
            request.session['username'] = username
            request.session.modified = True
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)