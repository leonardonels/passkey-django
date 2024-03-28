# mysite

WARNING: Passkey sign-up is not implemented yet so to use passkey create a profile with username and password first. From there you can test otp functionality as well as passkeys.

    To test it by yourself:
      1. clone this repository
      2. highly suggested to create a virtuale enviroment, 'pipenv' was used during developement
      3. if you have decided to use pipenv enter the virtual enviroment
         $ pipenv shell
      4. install all required packages, they are stored in the requirements.txt file
         $ pip install -r requirements.txt
      5. start the server
         $ python manage.py runserver
      6. to test it go to http://localhost:8000
         i know that tecnically localhost:8000 and 127.0.0.1:8000 are almost the same, 
         but localhost is recognised as a trusted source, 127.0.0.1:8000 is not and webauth features would not work

![Screenshot 2024-03-27 alle 10 51 19](https://github.com/leonardonels/mysite/assets/81677769/2aeef6b5-d33f-41db-82c2-b69c248b5d57)
![Screenshot 2024-03-27 alle 10 52 00](https://github.com/leonardonels/mysite/assets/81677769/7396a629-a5d9-4387-aeae-b66261a041bb)
![Screenshot 2024-03-27 alle 10 52 59](https://github.com/leonardonels/mysite/assets/81677769/0bfc6bfe-d210-499a-8cc6-34979462af02)
![Screenshot 2024-03-27 alle 10 53 04](https://github.com/leonardonels/mysite/assets/81677769/e7e56faf-b66e-4d31-8912-ed619a51b6fb)
![Screenshot 2024-03-27 alle 10 53 15](https://github.com/leonardonels/mysite/assets/81677769/d11fcd7d-0dec-48d0-88ad-4204d2e43d2f)
