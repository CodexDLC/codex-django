from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="CabinetSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cabinet_name",
                    models.CharField(
                        default="Кабинет",
                        max_length=100,
                        verbose_name="Cabinet name",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        upload_to="cabinet/",
                        verbose_name="Logo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cabinet settings",
                "verbose_name_plural": "Cabinet settings",
            },
        ),
    ]
