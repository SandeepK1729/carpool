from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.

from django.db import models
from datetime import date

from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.core.mail import send_mail


sex_choice = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    username        = models.CharField(
                        _("Username"),
                        max_length=150,
                        unique=True,
                        help_text=_(
                            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
                        ),
                        validators=[username_validator],
                        error_messages={
                            "unique": _("A user with that username already exists."),
                        },
                    )
    password        = models.CharField(_("password"), max_length=128)
    first_name      = models.CharField(_("first name"), max_length=150, blank=True)
    last_name       = models.CharField(_("last name"), max_length=150, blank=True)
    mobile_number   = models.CharField(
                        blank = False,
                        unique = True, 
                        max_length = 10,
                        help_text = "Enter 10 digit phone number only"
                    )
    email           = models.EmailField(_("email address"), blank=True)
    gender      = models.CharField(
                    max_length=50, 
                    choices=sex_choice, 
                    default='Male'
                )
    
    address     = models.CharField(max_length=100, null=False)
    city        = models.CharField(max_length=100, null=False)
    state       = models.CharField(max_length=100, null=False)
    is_staff        = models.BooleanField(
                        _("staff status"),
                        default = False,
                    )
    is_active       = models.BooleanField(
                        _("active"),
                        default = True,
                    )
    
    # groups          = models.ManyToManyField("group.Group", related_name = "members", blank = True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"

    def get_all_groups(self):
        return self.groups

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Customer(AbstractUser):
    # CustomUser model will be act as General class of parent
    pass


class Mycar(models.Model):
    cust=models.ForeignKey(Customer, max_length=100, blank=True, null=True, on_delete=models.SET_NULL)
    car_num=models.CharField(max_length=10, unique=True)
    company=models.CharField(max_length=30)
    car_name=models.CharField(max_length=30)
    car_type=models.CharField(max_length=30)
    from_place=models.CharField(max_length=30)
    to_place=models.CharField(max_length=30)
    from_date=models.DateField(null=True)
    to_date=models.DateField(null=True)
    price=models.FloatField()
    car_img = models.ImageField(upload_to="cars",default="", null = True,blank = True)

    def __str__(self):
        return self.car_num
    
    @property
    def imageURL(self):
        try:
            url = self.car_img.url
        except:
            url = ''
        return url


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.car_img.path)
        if img.height > 1500 or img.width > 1500:
            output_size = (1500, 1500)
            img.thumbnail(output_size)
            img.save(self.car_img.path)

class ContactUs(models.Model):
    name=models.CharField(max_length=80)
    email=models.EmailField(max_length=80, unique=True, blank=False)
    phone=models.CharField(max_length=11, null=False, blank=True)
    msg=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Booking(models.Model):
    name=models.ForeignKey(Customer,on_delete=models.SET_NULL, null=True)
    car=models.ForeignKey(Mycar,on_delete=models.SET_NULL, null=True)
    contact=models.CharField(max_length=11,null=False)
    email=models.EmailField(max_length=80)
    pickup=models.DateField()
    dropoff=models.DateField()
    pick_add=models.CharField(max_length=100, null=False)
    drop_add=models.CharField(max_length=100, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)