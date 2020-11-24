import sys
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect
from django.views import generic
from users.models import *
from users.forms import *
from food import models as food_models
from search import api_calls


# Create your views here.
def homepage(request):
    context = {}

    return render(request, 'homepage.html', context=context)


# Admin pages
def admin_analytics(request):
    context = {}

    return render(request, 'admin_analytics.html', context=context)


def admin_add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()

            if user.is_member:
                member = Member(user=user, coach_id=form.cleaned_data.get('coach_id'))
                member.save()
            if user.is_coach:
                coach = Coach(user=user)
                coach.save()
            if user.is_admin:
                user.is_staff = True
                user.save()

            return HttpResponseRedirect(reverse('admin_add_user') + '?s=1')
    else:
        form = AddUserForm()

    context = {
        'form': form,
        's': request.GET.get('s', '0')
    }
    return render(request, 'admin_add_user.html', context=context)


# Coach pages


# Member pages
def meal_add(request):
    if request.method == 'POST':
        form = AddMealForm(request.POST)
        if form.is_valid():
            timestamp = form.cleaned_data.get('date')
            member = Member.objects.get(user=request.user)

            meal = food_models.Meal(member_id=member.id, timestamp=timestamp)
            meal.save()

            return HttpResponseRedirect(reverse('member_meal_add_food', kwargs={'id': meal.id}))

    else:
        form = AddMealForm()

    context = {
        'form': form
    }

    return render(request, 'member_meal_add.html', context=context)


def meal_add_food(request, id):
    meal = food_models.Meal.objects.get(id=id)

    if request.method == 'POST':
        form = AddFoodForm(request.POST)
        if form.is_valid():
            food_id = form.cleaned_data.get('food_id')
            food_data = api_calls.get_food(food_id)

            name = food_data.get('name')

            food_product, created = food_models.FoodProduct.objects.get_or_create(
                product_name=name,
                fdc_id=food_id
            )

            if created:
                # foodproduct not already in db
                ingredients = food_data.get('ingredients')

                for ingr_key in ingredients:
                    ingredient = ingredients.get(ingr_key)
                    ingr_name = ingredient.get('name')

                    ingredient_obj, ingr_created = food_models.Ingredient.objects.get_or_create(
                        ingredient_name=ingr_name
                    )

                    food_product.ingredients.add(ingredient_obj)

                nutrients = food_data.get('nutrients')

                for nutr_key in nutrients:
                    nutrient = nutrients.get(nutr_key)
                    nutr_name = nutrient.get('name')
                    nutr_unit = nutrient.get('unit')
                    nutr_amount = nutrient.get('amount')

                    nutr_obj, nutr_created = food_models.Nutrient.objects.get_or_create(
                        nutrient_name=nutr_name
                    )

                    nutr_through = food_models.FoodNutrient.objects.create(
                        nutrient=nutr_obj, food_product=food_product, amount=nutr_amount, unit=nutr_unit
                    )

                food_product.save()

            portions = food_data.get('portions')
            portion_id = int(form.cleaned_data.get('portion_id'))
            portion_info = portions.get(portion_id)
            food_portion = food_models.FoodPortion.objects.create(description=portion_info.get('description'),
                                                                  gram_weight=portion_info.get('weight'))

            meal_food_serving = food_models.MealFoodServings.objects.create(meal=meal, food_product=food_product,
                                                                            portion=food_portion, servings=form.cleaned_data.get('servings'))

            return HttpResponseRedirect(reverse('member_meal_add_food', kwargs={'id': id}))
    else:
        form = AddFoodForm()

    context = {
        'form': form,
        'meal': meal
    }

    return render(request, 'member_meal_add_food.html', context=context)


class MemberListView(generic.ListView):
    model = Member

    def get_queryset(self):
        coach = Coach.objects.get(user_id=self.request.user)
        return Member.objects.filter(coach_id=coach)


class MemberDetailView(generic.DetailView):
    model = Member
