from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html',{
        'form': UserCreationForm
        }) 
    else:
       if request.POST['password1'] == request.POST['password2']:
        try:
            user= User.objects.create_user(username=request.POST['username'],
                                        password=request.POST['password1'])
            user.save()
            login(request, user)#genera la cookies para la sesion del usuario (session)
            return redirect('index')
        except:
            return render(request, 'signup.html',{
            'form': UserCreationForm,
            'error' : 'Username already exists'
            }) 
        
    return render (request, 'signup.html',{
    'form': UserCreationForm,
    'error': 'Password do not match'
    }) 


def index(request):
    return render(request, 'index.html')


@login_required #Se agrega para proteger las rutas ya que se podria acceder sin estar logeado
def task(request):
    tasks=Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'task.html',{
        'tasks':tasks
    })


@login_required
def task_detail(request, task_id):
    task= get_object_or_404(Task, pk=task_id, user=request.user)
    

    if request.method == 'GET':
        form = TaskForm(instance=task)    
        return render(request, 'task_detail.html', {
            'tasks':task,
            'form':form

        })
    else:
        try:
            form = TaskForm(request.POST,instance=task)
            form.save()
            return redirect ('task')
        except ValueError:
            return render(request, 'task_detail.html',{
                'tasks':task,
                'form':form,
                'error':'Error updating task'
            })

@login_required
def task_completed(request):
    tasks=Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'task.html',{
        'tasks':tasks
    })


    
@login_required
def signout(request):
    logout(request)
    return redirect('index')


def signin(request):
    if request.method == 'GET':
        return render(request,'signin.html',{
        'form':AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html',{
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('task')

   
@login_required
def create_task(request):

    if request.method =='GET':
        return render(request, 'create_task.html',{
        'form':TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST) #recibo los datos y los paso a la clase TaskForm y genera un formulario
            new_task = form.save(commit=False)# uso el metodo save del formulario para que me regrese los datos y evito que los guarde
            new_task.user=request.user #le  agrego el usuario
            new_task.save()
            return redirect('task')
        except ValueError:
            return render(request, 'create_task.html',{
            'form':TaskForm,
            'error':'Please provide valida data '
            })


@login_required
def complete_task(request, task_id):
    task=get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method =='POST':
        task.datecompleted=timezone.now()
        task.save()
        return redirect('task')

@login_required
def delete_task(request, task_id):
    task=get_object_or_404(Task,pk=task_id, user=request.user)
    if request.method =='POST':
        task.delete()
        return redirect('task')




    