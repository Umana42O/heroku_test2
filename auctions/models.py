from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Auctions(models.Model):
    title = models.CharField(max_length=255, null=False)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    active = models.BooleanField(default=True, null=False)
    initial_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, default="https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png")
    
    def save(self, *args, **kwargs):
        # Si current_price no está establecido, establecerlo en initial_price
        if self.current_price is None:
            self.current_price = self.initial_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.owner}"

# Ofertas
class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    auctions = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')

    def __str__(self):
        return f"{self.user} - {self.auctions} - {self.amount}"

    def save(self, *args, **kwargs):
        self.auctions.current_price = self.amount
        self.auctions.save()
        super().save(*args, **kwargs)

    
# Comentarios
class Comment(models.Model):
    content = models.TextField()
    auctions = models.ForeignKey(Auctions, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user} - {self.auctions} - {self.content}"

# Watchlist
class Watchlist(models.Model):
    auctions = models.ForeignKey(Auctions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} - {self.auctions}"