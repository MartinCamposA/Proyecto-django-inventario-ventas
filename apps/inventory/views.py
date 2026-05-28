from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Category, Product
from .forms import CategoryForm, ProductForm


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
    """Lista de productos con búsqueda y filtro por categoría."""
    query = request.GET.get("q", "")
    category_id = request.GET.get("category", "")

    products = Product.objects.select_related("category").all()

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    categories = Category.objects.filter(is_active=True)

    return render(request, "inventory/product_list.html", {
        "products": products,
        "categories": categories,
        "query": query,
        "selected_category": category_id,
        "total_products": products.count(),
    })


@login_required
def product_create(request):
    """Crear un producto nuevo."""
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"✅ Producto '{product.name}' creado correctamente.")
            return redirect("inventory:product_list")
    else:
        form = ProductForm()

    return render(request, "inventory/product_form.html", {
        "form": form,
        "title": "Agregar Producto",
        "button_text": "Crear Producto",
    })


@login_required
def product_edit(request, pk):
    """Editar un producto existente."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Producto '{product.name}' actualizado.")
            return redirect("inventory:product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "inventory/product_form.html", {
        "form": form,
        "title": f"Editar: {product.name}",
        "button_text": "Guardar Cambios",
        "product": product,
    })


@login_required
def product_toggle(request, pk):
    """Activa o desactiva un producto rápidamente."""
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    estado = "activado" if product.is_active else "desactivado"
    messages.success(request, f"Producto '{product.name}' {estado}.")
    return redirect("inventory:product_list")


# ─── CATEGORÍAS ───────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    """Lista de categorías."""
    categories = Category.objects.all()
    return render(request, "inventory/category_list.html", {
        "categories": categories,
    })


@login_required
def category_create(request):
    """Crear una categoría nueva."""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"✅ Categoría '{category.name}' creada.")
            return redirect("inventory:category_list")
    else:
        form = CategoryForm()

    return render(request, "inventory/category_form.html", {
        "form": form,
        "title": "Agregar Categoría",
        "button_text": "Crear Categoría",
    })


@login_required
def category_edit(request, pk):
    """Editar una categoría existente."""
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Categoría '{category.name}' actualizada.")
            return redirect("inventory:category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "inventory/category_form.html", {
        "form": form,
        "title": f"Editar: {category.name}",
        "button_text": "Guardar Cambios",
    })