from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Building(models.Model):
    """Модель для хранения информации о здании"""
    address = models.TextField(
        verbose_name="Адрес",
        help_text="Введите адрес здания",
    )
    latitude = models.FloatField(
        verbose_name="Широта",
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.FloatField(
        verbose_name="Долгота",
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )

    class Meta:
        verbose_name = "Здание"
        verbose_name_plural = "Здания"

    def __str__(self):
        return self.address

class Activity(models.Model):
    """Модель для классифицирования рода деятельности организаций"""
    name = models.CharField(
        max_length=100,
        verbose_name="Название деятельности",
        help_text="Введите название деятельности",
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская деятельность"
    )
    level = models.IntegerField(
        default=1,
        verbose_name="Уровень вложенности",
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )

    class Meta:
        verbose_name = "Деятельность"
        verbose_name_plural = "Виды деятельности"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автоматически вычисляем уровень вложенности
        if self.parent:
            self.level = self.parent.level + 1
            if self.level > 3:
                raise ValueError("Максимальный уровень вложенности - 3")
        else:
            self.level = 1
        super().save(*args, **kwargs)

class Organization(models.Model):
    """Модель для хранения карточки организации"""
    name = models.CharField(
        max_length=100,
        verbose_name="Название",
        help_text="Название организации"
    )
    phone_numbers = models.JSONField(
        verbose_name="Номера телефонов",
        help_text="Список номеров телефонов",
        default=list
    )
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='organizations',
        verbose_name="Здание"
    )
    activities = models.ManyToManyField(
        Activity,
        related_name='organizations',
        verbose_name="Виды деятельности"
    )

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name
