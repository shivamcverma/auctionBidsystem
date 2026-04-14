from django.contrib import admin

from myapp.models import AuctionItem, Category, Bid, UserProfile

# Register your models here.
admin.site.register(Category)
admin.site.register(AuctionItem)
admin.site.register(Bid)
admin.site.register(UserProfile)