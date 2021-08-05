from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name=models.CharField(max_length=128,unique=True)
    views=models.IntegerField(default=0)
    likes=models.IntegerField(default=0)
    slug=models.SlugField(unique=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super(Category,self).save(*args,**kwargs)

    class Meta:
        verbose_name_plural='Categories'

    def __str__(self):
        return self.name

class Page(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    title=models.CharField(max_length=128)
    url=models.URLField()
    views=models.IntegerField(default=0)
    likeNumber=models.IntegerField(default=0)

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    likedCategories=models.ManyToManyField(Category,blank=True,default='')
    #userName = models.CharField(max_length=150)

    def __str__(self):
        return self.user.username

class Comment(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    text = models.TextField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True)
    page=models.CharField(max_length=100)

    def __str__(self):
        return self.text[:20]
        