from django.shortcuts import render, redirect
from django.views import View
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from requests import request
from django.contrib.auth.hashers import make_password
from website.models import Customer, Mycar, ContactUs, Booking
from django.contrib.auth.decorators import login_required

from .forms import CustomerCreationForm

@login_required
def home(request):
    return render(request, "home.html")

#Function to help register the user
def Register(request):
    form = CustomerCreationForm()

    if request.method == "POST":
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect("login")
        else:
            messages.warning(request, "Please correct the error below.")

    return render(request, "register.html", {"form": form})


#Function to help user contact the admin
def Contactus(request):
    if request.method=="GET":
        return render(request, "contact.html")
    
    if request.method=="POST":
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        msg=request.POST['msg']

        if len(phone)!=10 or phone.isdigit()==False:
            messages.warning(request, "The phone number provided is not 10 digits!")
        elif phone.startswith(('1', '2', '3', '4', '5', '0')):
            messages.warning(request, "The phone number provided is not valid!")
        else:
            contact_us = ContactUs.objects.create(name=name, email=email, phone=phone, msg=msg)
            contact_us.save()
            messages.success(request, "Thank you for contacting us, we will reach you soon.")

        return render(request, "contact.html")

#Function to search the car on search.html page and redirect to the searched_cars.html
def Search(request):
    if request.method=="GET":
        return render(request, "search.html")
    
    if request.method=="POST":
        from_place=request.POST['from_place']
        to_place=request.POST['to_place']
        from_date=request.POST['from_date']
        to_date=request.POST['to_date']
        cars = Mycar.objects.filter(from_place=from_place,to_place=to_place,from_date=from_date, to_date=to_date)

        context = {'cars': cars}
        return render(request, "searched_cars.html", context)
        
#Function to show details of the car to the user, but if the user is not logged in then take to login page    
@login_required
def Cardetails(request,car_id):
    if request.method=="GET":
        car=Mycar.objects.get(pk=car_id)
        context={'car':car}
        return render(request,"cardetails.html",context)
    
    #Function to book the car
    if request.method=="POST":
        #name=request.POST['name']
        contact=request.POST['contact']
        email=request.POST['email']
        pickup=request.POST['pickup']
        dropoff=request.POST['dropoff']
        pick_add=request.POST['pick_add']
        drop_add=request.POST['drop_add']
        if len(contact)!=10 or contact.isdigit()==False:
            messages.warning(request, "The phone number provided is not 10 digits!")
        elif contact.startswith(('1', '2', '3', '4', '5', '0')):
            messages.warning(request, "The phone number provided is not valid!")
        else:
            user = request.user
            print(user)
            cust=Customer.objects.get(usern=user)
            print(cust)
            car=Mycar.objects.get(pk=car_id)
            overlap_bookings = Booking.objects.filter(car=car, pickup=pickup, dropoff=dropoff)
            if overlap_bookings.exists():
                messages.error(request, "The car is not available for the selected dates.")
                return redirect('cardetails', car_id=car_id)
            
            cars = Booking.objects.create(name=cust, car=car, email=email, contact=contact,pickup=pickup,dropoff=dropoff,pick_add=pick_add,drop_add=drop_add)
            cars.save()
            #messages.success(request, "Your booking has been submitted successfully!")
            return redirect('bookedcar', car_id=car_id)
    return redirect('cardetails', car_id=car_id)




#Function to show the booked cars, booked by the user
def Booked(request,car_id):
    if request.method=="GET":
        if request.user.is_authenticated:
            messages.success(request, "Your booking has been done successfully!")
            user = request.user
            cust=Customer.objects.get(usern=user)
            
            book=Booking.objects.get(car=car_id, name=cust)
            print(book)
            context={'book':book}
            return render(request, "booked.html", context)




#Function to show dashboard to the logged in users
def dash(request):
    if request.user.is_authenticated:
        print(request.user)
        return render(request, "dashboard.html")



#Function to show logged in user's bookings from the dashboard
def MyBookings(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            custs=Booking.objects.filter(name=request.user)
            context={'custs':custs}
            return render(request, "mybooking.html",context)

#Function to show logged in user's account details
@login_required
def MyAccount(request):
    customer = request.user

    return render(request, "myaccount.html", {
        'cust' : customer,
    })



#Function to show logged in user's cars booked by other customer's
@login_required
def CustomerBookings(request):
    customer = request.user
    mybook   = Booking.objects.filter(name=customer)
    mycar    = Mycar.objects.filter(cust=customer)
    otherbookings = Booking.objects.filter(car__in=mycar).exclude(name=customer)

    return render(request, "cust_booking.html", {
        'otherbookings': otherbookings,
    })



#Function to show logged in user, their added cars
@login_required
def MyCarList(request):
    custs=Mycar.objects.filter(cust=request.user)
    context={'custs': custs}
    return render(request, "mycar_list.html", context)



#Function to show all the cars to the logged in or unloggedin users on the allcars.html
def Cars(request):
    if request.method == 'GET':
        mycars=Mycar.objects.all()
        context={'mycars': mycars}
        return render(request, "allcars.html", context)
    
    #if request.method == 'POST':
    #    if request.user.is_authenticated:
    #        return render("")


#Function to add user's car in the database
def Addcar(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, "addmycar.html")
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            car_num=request.POST['car_num']
            car_name=request.POST['car_name']
            from_place=request.POST['from_place']
            to_place=request.POST['to_place']
            car_type=request.POST['car_type']
            company=request.POST['company']
            price=request.POST['price']
            from_date=request.POST['from_date']
            to_date=request.POST['to_date']
            car_img=request.FILES['car_img']
            custom=Customer.objects.get(usern=request.user)
            print(custom)
            car=Mycar.objects.filter(car_num=car_num)
            if car.exists():
                messages.warning(request, 'Car Already exists')
                return redirect('addmycar')
            obj=Mycar.objects.create(car_num=car_num,from_date=from_date,to_date=to_date,car_name=car_name,from_place=from_place,to_place=to_place,car_type=car_type,company=company, price=price, car_img=car_img, cust=custom)
            obj.save()
            return redirect('dashboard') 
                     
    return render(request,"addmycar.html")
