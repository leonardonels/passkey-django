from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import image_link
from .form import ImageForm

def create(request):
    if request.method == 'POST':
        form = ImageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/home')  # Puoi cambiare il percorso di reindirizzamento come desideri
    else:
        form = ImageForm()

    return render(request, 'create.html', {'form': form})


'''
def create(request):
    if request.method == 'POST':
        form = ImageForm(request.POST)
        if form.is_valid():
            form.save()
            # Recupera l'ultima immagine salvata
            last_img = image_link.objects.last()
            if last_img:
                # Se l'immagine esiste, puoi fare qualcosa
                # come reindirizzare l'utente o mostrare un messaggio di successo
                return redirect('/home')  # Reindirizza alla tua homepage o a un'altra pagina desiderata
            else:
                # Se l'immagine non esiste, potrebbe esserci stato un errore durante il salvataggio
                # Puoi gestire l'errore qui o fornire un messaggio all'utente
                pass
    else:
        form = ImageForm()

    return render(request, 'create.html', {'form': form})
    '''