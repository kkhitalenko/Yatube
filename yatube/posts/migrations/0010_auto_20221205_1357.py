# Generated by Django 2.2.16 on 2022-12-05 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_follow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=200, verbose_name='Комментарий'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique following'),
        ),
    ]