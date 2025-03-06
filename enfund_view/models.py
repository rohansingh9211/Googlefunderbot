from django.db import models

class User(models.Model):
    email=models.EmailField(null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, blank=True)
    social_id = models.CharField(max_length=255, blank=False, unique=True)
    account_image = models.URLField(null=False, blank=False)
    

class googledrive(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    drive_id = models.CharField(max_length=255, null=False, blank=False, unique=True)

class Message(models.Model):
    username = models.CharField(max_length=100)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.text[:20]}"
