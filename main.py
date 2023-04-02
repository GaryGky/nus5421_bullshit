############################################################################
## Django ORM Standalone Python Template
############################################################################
""" Here we'll import the parts of Django we need. It's recommended to leave
these settings as is, and skip to START OF APPLICATION section below """

# Turn off bytecode generation
import sys

from django.db.models.functions import ExtractYear, TruncDate
from memory_profiler import profile

sys.dont_write_bytecode = True

# Django specific settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django

django.setup()

# Import your models for use in your script
from db.models import *
from django.db.models import Sum, F, Q


############################################################################
################# START OF APPLICATION
@profile
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
            Subtotal=Sum(F('unitprice') * F('quantity') * (1 - F('discount')), output_field=models.FloatField())
        )
        .order_by('OrderID')
    )
    print(subtotal_by_order.query)
    print(subtotal_by_order)
    return


@profile
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
    orders = Orderdetails.objects.select_related('OrderID_id').filter(
        OrderID_id__shippeddate__isnull=False,
        OrderID_id__shippeddate__range=['1996-12-24', '1997-09-30']
    ) \
        .annotate(year=ExtractYear('OrderID_id__shippeddate')) \
        .annotate(ShippedDate=TruncDate('OrderID_id__shippeddate')) \
        .annotate(
        Subtotal=Sum(F('unitprice') * F('quantity') * (1 - F('discount')),
                     output_field=models.FloatField())). \
        values('OrderID_id__shippeddate', 'OrderID_id__orderid', 'Subtotal', 'year'). \
        order_by('ShippedDate')
    print(orders.query)
    print(orders)
    return


@profile
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
            products__discontinued=1
        )
        .annotate(
            CategoryName=F('categoryname'),
        )
        .values(
            'products__productid',
            'products__productname',
            'products__supplierid',
            'products__categoryid',
            'products__quantityperunit',
            'products__unitsinstock',
            'products__unitsonorder',
            'products__reorderlevel',
            'products__discontinued',
            'CategoryName'
        )
        .order_by('products__productname')
    )

    print(categories.query)
    print(categories)


@profile
def listOfProducts():
    """
    select distinct b.*, a.CategoryName
    from Categories a
    inner join Products b on a.CategoryID = b.CategoryID
    where b.Discontinued = 1
    order by b.ProductName;
    :return:
    """

    categories = Products.objects.filter(discontinued=1) \
        .select_related('categoryid').annotate().order_by('productname') \
        .values('id', 'productname', 'categoryid__categoryid', 'categoryid__categoryname')
    print(categories.query)
    print(categories)


@profile
def currentProductList():
    """
    select ProductID, ProductName
    from products
    where Discontinued = 1
    order by ProductName;
    :return:
    """
    products = (
        Products.objects.filter(
            discontinued=1
        )
        .values(
            'productid',
            'productname'
        )
        .order_by('productname')
    )
    print(products.query)
    print(len(products.values()))


if __name__ == '__main__':
    from datetime import datetime

    func_list = [orderSubTotals, salesByYear, employeeSalesByCountry, listOfProducts, currentProductList]
    for func in func_list:
        start_time = datetime.now()
        func()
        execute_time = datetime.now() - start_time
        print(func.__name__, "execute time: ", execute_time)
