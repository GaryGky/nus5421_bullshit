############################################################################
## Django ORM Standalone Python Template
############################################################################
""" Here we'll import the parts of Django we need. It's recommended to leave
these settings as is, and skip to START OF APPLICATION section below """

# Turn off bytecode generation
import sys

from django.db.models.functions import ExtractYear, TruncDate

sys.dont_write_bytecode = True

# Django specific settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

# Import your models for use in your script
from db.models import *
from django.db.models import Sum, F


############################################################################
################# START OF APPLICATION

def orderSubTotals():
    """
        select OrderID, format(sum(UnitPrice * Quantity * (1 - Discount)), 2) as Subtotal
        from orderdetails
        group by OrderID
        order by OrderID;
        """
    subtotal_by_order = (
        Orderdetails.objects
        .values('OrderID')
        .annotate(
            Subtotal=Sum(F('UnitPrice') * F('Quantity') * (1 - F('Discount')), output_field=models.FloatField())
        )
        .order_by('OrderID')
    )
    print(subtotal_by_order.query)
    print(subtotal_by_order)
    return


def salesByYear():
    """
    select distinct date(a.ShippedDate) as ShippedDate,
                a.OrderID,
                b.Subtotal,
                year(a.ShippedDate) as Year
    from Orders a
             inner join
         (
             select distinct OrderID,
                             format(sum(UnitPrice * Quantity * (1 - Discount)), 2) as Subtotal
             from orderdetails
             group by OrderID) b on a.OrderID = b.OrderID
    where a.ShippedDate is not null
      and a.ShippedDate between date('1996-12-24') and date('1997-09-30')
    order by a.ShippedDate;
    :return:
    """
    orders = (
        Orders.objects.filter(
            ShippedDate__isnull=False,
            ShippedDate__range=('1996-12-24', '1997-09-30')
        )
        .annotate(
            Year=ExtractYear('ShippedDate'),
            ShippedDate=TruncDate('ShippedDate')
        )
        .values(
            'ShippedDate',
            'OrderID',
            'Year'
        )
        .annotate(
            Subtotal=Sum('order_details__UnitPrice' * 'order_details__Quantity' * (1 - 'order_details__Discount'))
        )
        .order_by('ShippedDate')
        .distinct('ShippedDate', 'OrderID', 'Subtotal', 'Year')
    )
    print(orders.query)
    print(orders)
    return


def employeeSalesByCountry():
    """
    select distinct b.*, a.CategoryName
    from Categories a
    inner join Products b on a.CategoryID = b.CategoryID
    where b.Discontinued = 'N'
    order by b.ProductName;
    :return:
    """
    categories = (
        Categories.objects.filter(
            products__Discontinued='N'
        )
        .annotate(
            CategoryName=F('CategoryName'),
        )
        .values(
            'products__ProductID',
            'products__ProductName',
            'products__SupplierID',
            'products__CategoryID',
            'products__QuantityPerUnit',
            'products__UnitPrice',
            'products__UnitsInStock',
            'products__UnitsOnOrder',
            'products__ReorderLevel',
            'products__Discontinued',
            'CategoryName'
        )
        .order_by('products__ProductName')
        .distinct('products__ProductID')
    )
    print(categories.query)
    print(categories)


def listOfProducts():
    """
    select distinct b.*, a.CategoryName
    from Categories a
    inner join Products b on a.CategoryID = b.CategoryID
    where b.Discontinued = 'N'
    order by b.ProductName;
    :return:
    """
    categories = (
        Categories.objects.filter(
            products__Discontinued='N'
        )
        .annotate(
            CategoryName=F('CategoryName')
        )
        .values(
            'products__ProductID',
            'products__ProductName',
            'products__SupplierID',
            'products__CategoryID',
            'products__QuantityPerUnit',
            'products__UnitPrice',
            'products__UnitsInStock',
            'products__UnitsOnOrder',
            'products__ReorderLevel',
            'products__Discontinued',
            'CategoryName'
        )
        .order_by('products__ProductName')
        .distinct('products__ProductID')
    )

    print(categories.query)
    print(categories)


def currentProductList():
    """
    select ProductID, ProductName
    from products
    where Discontinued = 'N'
    order by ProductName;
    :return:
    """
    products = (
        Products.objects.filter(
            Discontinued='N'
        )
        .values(
            'ProductID',
            'ProductName'
        )
        .order_by('ProductName')
    )
    print(products.query)
    print(products)


if __name__ == '__main__':
    currentProductList()
