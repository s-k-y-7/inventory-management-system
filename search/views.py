from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Case, When, Value, IntegerField, Subquery, OuterRef
from django.db.models.functions import Coalesce
from products.models import Product
from stores.models import Inventory
from .serializers import ProductSearchSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductSearchAPIView(generics.ListAPIView):
    serializer_class = ProductSearchSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['store_id'] = self.request.query_params.get('store_id')
        return context

    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        
        # Keyword search
        q = self.request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(category__name__icontains=q)
            )
            
        # Filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__iexact=category)
            
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        store_id = self.request.query_params.get('store_id')
        in_stock = self.request.query_params.get('in_stock', '').lower() == 'true'
        
        if store_id:
            store_qty_subquery = Inventory.objects.filter(
                product=OuterRef('pk'),
                store_id=store_id
            ).values('quantity')[:1]
            
            queryset = queryset.annotate(store_quantity=Coalesce(Subquery(store_qty_subquery), 0))
            
            if in_stock:
                queryset = queryset.filter(store_quantity__gt=0)
        elif in_stock:
            queryset = queryset.filter(inventory_items__quantity__gt=0).distinct()

        # Sorting
        sort = self.request.query_params.get('sort', 'relevance')
        if sort == 'price':
            queryset = queryset.order_by('price')
        elif sort == '-price':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-id')
        elif sort == 'relevance':
            if q:
                queryset = queryset.annotate(
                    relevance=Case(
                        When(title__iexact=q, then=Value(3)),
                        When(title__istartswith=q, then=Value(2)),
                        When(title__icontains=q, then=Value(1)),
                        default=Value(0),
                        output_field=IntegerField(),
                    )
                ).order_by('-relevance', 'title')
            else:
                queryset = queryset.order_by('title')
                
        return queryset

class AutocompleteAPIView(APIView):
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q', '')
        if len(q) < 3:
            return Response([])
            
        prefix_matches = list(Product.objects.filter(title__istartswith=q).values_list('title', flat=True)[:10])
        
        if len(prefix_matches) < 10:
            general_matches = list(
                Product.objects.filter(title__icontains=q)
                .exclude(title__istartswith=q)
                .values_list('title', flat=True)[:10 - len(prefix_matches)]
            )
            results = prefix_matches + general_matches
        else:
            results = prefix_matches
            
        return Response(results)

