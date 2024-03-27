from django.shortcuts import render, get_object_or_404, redirect
from users.models import User
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import AttestationConveyancePreference, UserVerificationRequirement, PublicKeyCredentialDescriptor, PublicKeyCredentialType, UserVerificationRequirement
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.parse_registration_credential_json import parse_registration_credential_json
from webauthn.helpers.parse_authentication_credential_json import parse_authentication_credential_json
from mysite.settings import REPLYING_PARTY_ID, REPLYING_PARY_NAME, ORIGIN
from django.http import JsonResponse
import json, base64
from .models import Credential, TemporaryChallenge, User_Verification
from typing import List
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

@login_required
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
    )

    #create and save the challenge
    challenge = base64.b64encode(options.challenge).decode('utf-8')
    TemporaryChallenge.objects.create(user=user, challenge=challenge)

    return JsonResponse(json.loads(options_to_json(options)))

@login_required
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
    if not User_Verification.objects.filter(credential_id=new_credential.id).first():
        User_Verification.objects.create(
            value=True,
            user=user,
            credential=new_credential,
        )
    user.set_custom_backend()

    return JsonResponse({"verified":True})


def authentication(request):

    #get User informations
    username = request.session['username']
    user=get_object_or_404(User, username=username)

    #start the ceremony
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
        #REQUIRED = always ask for confermation, even if user is using a passkey that wont require it, a lazy approach, but works
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    #create and save the challenge
    challenge = options.challenge
    TemporaryChallenge.objects.create(user=user, challenge=base64.b64encode(challenge).decode('utf-8'))

    return JsonResponse(json.loads(options_to_json(options)))


def authentication_verification(request):

    #get User informations
    request_body=request.body.decode('utf-8')
    username = request.session['username']
    user=get_object_or_404(User, username=username)
    temp_challenge = TemporaryChallenge.objects.filter(user=user)
    challenge = base64.b64decode(temp_challenge.last().challenge.encode('utf-8'))
    temp_challenge.delete()

    #start registration flow
    try:
        request_credential=parse_authentication_credential_json(request_body)
        user_credential = Credential.objects.filter(user_id=user.id, credential_id=request_credential.raw_id).first()

        if not user_credential:
            raise Exception("User does not have credentials with give ID")

        user_verification=User_Verification.objects.filter(user=user, credential_id=user_credential.id).last()
        
        verification=verify_authentication_response(
            credential=request_credential,
            expected_challenge=challenge,
            expected_rp_id=REPLYING_PARTY_ID,
            expected_origin=ORIGIN,
            credential_public_key=user_credential.public_key,
            credential_current_sign_count=user_credential.sign_counts,
            require_user_verification=user_verification.value,
        )
    except Exception as err:
        return JsonResponse({"verified":False, "msg":str(err), "status":400})
    
    #updates credential for the user
    user_credential.sign_counts=verification.new_sign_count

    #custom login for verified user
    verified_user = authenticate(user_credential)
    login(request, verified_user)
    
    return JsonResponse({"verified":True})

login_required
def remove_passkey(request):
    if request.method == 'POST':
        Credential.objects.filter(user=request.user).delete()
        user=request.user
        user.reset_backend()
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