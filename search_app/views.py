from django.shortcuts import render
from shop.models import Product
from django.db.models import Q


# todo WHAT F*** Q? and name__contains
def searchResult(request):
    products = None
    query = None
    request_get = request.GET
    if 'q' in request.GET:
        query = request.GET.get('q')
        products = Product.objects.all().filter(Q(name__contains=query) | Q(description__contains=query))
    return render(request, 'search.html', {'query': query, 'products': products})
