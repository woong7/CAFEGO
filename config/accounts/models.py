from django.db import models

#user model 커스텀

class Blog(models.Model):
    title = models.CharField(max_length= 200)
    pub_date = models.DateField('date published')
    body = models.TextField()

    def __str__(self):
        return self.title

    #보여지는 글자수 줄이는 함수
    def summary(self):
        return self.body[:100] 