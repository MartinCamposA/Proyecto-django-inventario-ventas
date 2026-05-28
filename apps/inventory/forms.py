from django import forms
from .models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "Ej: Bebidas",
            }),
            "slug": forms.TextInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "ej: bebidas",
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category", "name", "sku",
            "purchase_price", "sale_price",
            "stock", "is_active"
        ]
        widgets = {
            "category": forms.Select(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
            }),
            "name": forms.TextInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "Ej: Coca-Cola 350ml",
            }),
            "sku": forms.TextInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "Ej: 7802800891001",
            }),
            "purchase_price": forms.NumberInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "0",
                "step": "1",
            }),
            "sale_price": forms.NumberInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "0",
                "step": "1",
            }),
            "stock": forms.NumberInput(attrs={
                "class": "w-full border-2 border-gray-200 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500",
                "placeholder": "0",
            }),
        }