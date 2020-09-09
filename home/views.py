import json

from django.contrib import messages
from django.http import HttpResponseRedirect, request
from django.http.response import JsonResponse
from django.shortcuts import render, HttpResponse
from django.template.loader import render_to_string

from product.models import Category, Product, Images, Comment, Variants
from .forms import SearchForm
from .models import Setting, ContactForm, ContactMessage


# Create your views here.
def index(request):
    setting = Setting.objects.get(pk=1)
    category = Category.objects.all()
    products_slider = Product.objects.all().order_by('id')[:4]
    products_latest = Product.objects.all().order_by('-id')[:4]
    products_picked = Product.objects.all().order_by('?')[:4]
    page = "home"
    context ={'setting': setting,
              'page': page,
              'category':category,
              'products_slider':products_slider,
              'products_latest': products_latest,
              'products_picked':products_picked,
              }
    return render(request, 'index.html', context)


def contactus(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = ContactMessage()
            data.name = form.cleaned_data['name']
            data.email = form.cleaned_data['email']
            data.subject = form.cleaned_data['subject']
            data.message = form.cleaned_data['message']
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            messages.success(request, 'Sizning xabaringiz qabul qilindi!Rahmat')
            return HttpResponseRedirect('/contact')
    setting = Setting.objects.get(pk=1)
    form = ContactForm
    context = {'setting': setting, 'form': form, }
    return render(request, 'contact.html', context)


def aboutus(request):
    setting = Setting.objects.get(pk=1)
    context = {'setting':setting,}
    return render(request, 'about.html', context)


def category_products(request, id, slug):
    category = Category.objects.all()
    #catdata = Category.objects.get(pk=1)
    products = Product.objects.filter(category_id=id)
    context = {
        'category': category,
        #'catdata': catdata,
        'products': products,
    }
    return render(request, 'category_products.html', context)

def search(request):
    if request.method=='POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            catid = form.cleaned_data['catid']
            if catid == 0:
                products = Product.objects.filter(title__icontains=query)
            else:
                products = Product.objects.filter(title__icontains=query, category_id=catid)

            category = Category.objects.all()
            context = {
                'products': products,
                'query': query,
                'category': category,
            }
            return render(request, 'search.html', context)
    return HttpResponseRedirect('/')


def search_auto(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        products = Product.objects.filter(title__icontains=q)
        results = []
        for rs in products:
            products_json = {}
            products_json = rs.title
            results.append(products_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def product_detail(request, id, slug):
    query = request.GET.get('q')
    category = Category.objects.all()
    product = Product.objects.get(pk=id)
    images = Images.objects.filter(product_id=id)
    comments = Comment.objects.filter(product_id=id, status='True')
    context = {
        'category': category,
        'product': product,
        'images': images,
        'comments': comments,
    }
    if product.variant !="None":
        if request.method == 'POST':
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(id=variant_id)
            colors = Variants.objects.filter(product_id=id, size_id=variant.size_id)
            sizes = Variants.objects.raw('SELECT * FROM product_variants WHERE product_id=%s GROUP  BY size_id',[id])
            query += variant.title + 'Size:' + str(variant.size) + 'Color:' + str(variant.color)
        else:
            variants = Variants.objects.filter(product_id=id)
            colors = Variants.objects.filter(product_id=id, size_id=variants[0].size_id)
            sizes = Variants.objects.raw('SELECT * FROM product_variants WHERE product_id=%s GROUP BY  size_id',[id])
            variant = Variants.objects.get(id=variants[0].id)
        context.update(
            {
                'sizes':sizes,
                'colors': colors,
                'variant': variant,
                'query': query,
            }
        )

    return render(request, 'product_detail.html', context)


def ajaxcolor(request):
    data = {}
    if request.POST.get('action')=='post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string('color_list.html', context)}
        return JsonResponse(data)
    return JsonResponse(data)

