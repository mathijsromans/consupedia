import logging
import uuid
from product.algorithms import ProductChooseAlgorithm

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView, UpdateView

from product.models import UserPreferences
from product.models import Product
from product.algorithms import generate_sorted_list
from website import settings

logger = logging.getLogger(__name__)


# This class defines a view for a certain URL
class MainView(TemplateView):
    template_name = 'website/index.html' # the template that will be used to render the page (in this case website/templates/website/index.html)

    @staticmethod
    def get_anonymous_group():
        group, created = Group.objects.get_or_create(name="anonymous")
        return group

    @staticmethod
    def create_anonymous_user(request):
        username = uuid.uuid4().hex[:10]
        email = username + '@anonymous.com'
        user = User.objects.create(username=username, email=email)
        password = uuid.uuid4().hex
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        login(request, user)
        group = MainView.get_anonymous_group()
        user.groups.add(group)
        return user

    # Specifies variables that can be used in the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated():
            user = self.create_anonymous_user(self.request)
        else:
            user = self.request.user
        up, created = UserPreferences.objects.get_or_create(user=user)
        product_list = Product.objects.all()
        # product_list = generate_sorted_list(product_list, up)
        context['recommended_product'] = product_list[0] if product_list else None
        context['all_products'] = product_list
        context['userPreference'] = up
        return context


class ContactView(TemplateView):
    template_name = 'website/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_email'] = settings.CONTACT_EMAIL
        return context


class UserProfileView(SuccessMessageMixin, UpdateView):
    model = User
    template_name = 'website/userprofile.html'
    fields = ['username', 'first_name', 'last_name', 'email']
    success_message = 'Userprofile saved'

    def get_context_data(self, **kwargs):
        if not self.request.user == self.get_object():
            raise PermissionDenied
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        if self.request.user != form.instance:
            raise PermissionDenied
        email = form.cleaned_data['email']
        users = User.objects.exclude(id=self.request.user.id).filter(email=email)
        if users.exists():
            form.add_error('email', 'Email is already used by another user.')
            logger.info('email is already used by another user')
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return '/userprofile/' + str(self.request.user.id) + '/'
