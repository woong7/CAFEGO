# Generated by Django 3.2.6 on 2021-08-08 15:41

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CafeList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='카페 이름')),
                ('address', models.CharField(max_length=50, verbose_name='카페 주소')),
                ('location_x', models.FloatField(default=0, verbose_name='카페 위도')),
                ('location_y', models.FloatField(default=0, verbose_name='카페 경도')),
                ('cafe_stars', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='카페 별점')),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emoticon_list', models.ImageField(upload_to='media/map/%Y/%m/%d')),
                ('level', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_stars', models.CharField(choices=[('⭐', '⭐'), ('⭐⭐', '⭐⭐'), ('⭐⭐⭐', '⭐⭐⭐'), ('⭐⭐⭐⭐', '⭐⭐⭐⭐'), ('⭐⭐⭐⭐⭐', '⭐⭐⭐⭐⭐')], default='⭐⭐⭐⭐⭐', max_length=20, verbose_name='리뷰 별점')),
                ('content', models.TextField(verbose_name='리뷰 내용')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='this_cafe', to='cafe.cafelist')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_person', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReviewPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to='media/review/%Y/%m/%d', verbose_name='리뷰 사진')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='this_review', to='cafe.review')),
                ('review_cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_cafe', to='cafe.cafelist')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='댓글 내용')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_comment', to='cafe.review')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_person', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]