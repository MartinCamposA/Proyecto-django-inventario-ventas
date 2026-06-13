from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Category, Product
from .forms import CategoryForm, ProductForm


# ─── PRODUCTOS ────────────────────────────────────────────────────────────────

@login_required
def product_list(request):
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

    # Convierte a int para comparar fácil en el template
    selected_category_int = int(category_id) if category_id else None

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "inventory/product_list.html", {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": categories,
        "query": query,
        "selected_category": selected_category_int,
        "total_products": paginator.count,
    })


@login_required
def product_create(request):
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
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    estado = "activado" if product.is_active else "desactivado"
    messages.success(request, f"Producto '{product.name}' {estado}.")
    return redirect("inventory:product_list")


@login_required
def stock_adjustment(request):
    products = Product.objects.select_related("category").filter(
        is_active=True
    ).order_by("category__name", "name")

    if request.method == "POST":
        updated = 0
        errors = []

        for product in products:
            key = f"stock_{product.id}"
            new_stock = request.POST.get(key)

            if new_stock is None or new_stock == "":
                continue

            try:
                new_stock = int(new_stock)
                if new_stock < 0:
                    errors.append(f"'{product.name}': el stock no puede ser negativo.")
                    continue

                if new_stock != product.stock:
                    product.stock = new_stock
                    product.save(update_fields=["stock"])
                    updated += 1

            except ValueError:
                errors.append(f"'{product.name}': valor inválido.")

        if errors:
            for error in errors:
                messages.error(request, error)

        if updated > 0:
            messages.success(
                request,
                f"✅ Stock actualizado en {updated} producto{'s' if updated > 1 else ''}."
            )

        return redirect("inventory:stock_adjustment")

    grouped = {}
    for product in products:
        cat_name = product.category.name
        if cat_name not in grouped:
            grouped[cat_name] = []
        grouped[cat_name].append(product)

    return render(request, "inventory/stock_adjustment.html", {
        "grouped_products": grouped,
        "total_products": products.count(),
    })


# ─── CATEGORÍAS ───────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "inventory/category_list.html", {
        "categories": categories,
    })


@login_required
def category_create(request):
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
    
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Verificar si el producto tiene ventas asociadas
    if product.sale_items.exists():
        messages.error(
            request,
            f"❌ No se puede eliminar '{product.name}' porque tiene ventas registradas. "
            f"Puedes desactivarlo en su lugar."
        )
        return redirect("inventory:product_list")

    if request.method == "POST":
        nombre = product.name
        product.delete()
        messages.success(request, f"✅ Producto '{nombre}' eliminado correctamente.")
        return redirect("inventory:product_list")

    return render(request, "inventory/product_confirm_delete.html", {
        "product": product,
    })