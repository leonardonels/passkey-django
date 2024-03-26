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
from .models import Credential, TemporaryChallenge
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from typing import List
from django.contrib.auth import authenticate, login


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
    challenge = base64.b64encode(options.challenge).decode('utf-8')
    TemporaryChallenge.objects.create(user=user, challenge=challenge)

    return JsonResponse(json.loads(options_to_json(options)))

    
def registration_verification(request):

    #get User informations
    user=request.user

    #start registration flow
    request_body=request.body.decode('utf-8')
    try:
        credential=parse_registration_credential_json(request_body)
        temp_challenge = TemporaryChallenge.objects.filter(user=user)
        challenge = base64.b64decode(temp_challenge.last().challenge.encode('utf-8'))

        if temp_challenge is not None:
            verification=verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_rp_id=REPLYING_PARTY_ID,
                expected_origin=ORIGIN,
            )
            # Delete the temporary challenge from the database
            temp_challenge.delete()
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
                id=cred.credential_id,
                type=PublicKeyCredentialType.PUBLIC_KEY,
                transports=cred.get_transports()
            )
        )

    options=generate_authentication_options(
        rp_id=REPLYING_PARTY_ID,
        allow_credentials=allow_credentials,
    )

    #create and save the challenge
    challenge = options.challenge
    TemporaryChallenge.objects.create(user=user, challenge=base64.b64encode(challenge).decode('utf-8'))

    return JsonResponse(json.loads(options_to_json(options)))


def verify_authentication(request):

    request_body=request.body.decode('utf-8')
    username = request.session['username']
    user=get_object_or_404(User, username=username)
    temp_challenge = TemporaryChallenge.objects.filter(user=user)
    challenge = base64.b64decode(temp_challenge.last().challenge.encode('utf-8'))
    temp_challenge.delete()

    try:
        request_credential=parse_authentication_credential_json(request_body)
        user_credential = Credential.objects.filter(user_id=user.id, credential_id=request_credential.raw_id).first()

        if not user_credential:
            raise Exception("User does not have credentials with give ID")
        
        verification=verify_authentication_response(
            credential=request_credential,
            expected_challenge=challenge,
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
    if request.method == 'POST':
        username = request.POST.get('username')
        request.session['username']=username
        return render(request, 'login_with_passkey.html')
    return redirect('/login/')

def set_username_in_session(request):
    if request.method == 'POST':
        request_data=json.loads(request.body)
        username = request_data.get('username')
        if username:
            request.session['username'] = username
            request.session.modified = True
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def perform_webauthn_login(request):
    #if request.user.is_authenticated:
    #    return JsonResponse({"success": False, "message": "User is already authenticated"})

    #SOLUZIONE TEMPORANEA, COSI NON ESISTE!!!
    username = request.session['username']
    user=get_object_or_404(User, username=username)
    if user is not None:
        login(request, user)
        return JsonResponse({"success": True, "message": "Login successful"})
    else:
        return JsonResponse({"success": False, "message": "Login failed"})