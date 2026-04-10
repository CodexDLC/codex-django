# Generated manually for codex-django tracking.

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PageView",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("path", models.CharField(db_index=True, max_length=500, verbose_name="path")),
                ("date", models.DateField(db_index=True, verbose_name="date")),
                ("views", models.PositiveIntegerField(default=0, verbose_name="views")),
            ],
            options={
                "verbose_name": "Page view",
                "verbose_name_plural": "Page views",
                "ordering": ["-date", "-views", "path"],
            },
        ),
        migrations.AddConstraint(
            model_name="pageview",
            constraint=models.UniqueConstraint(fields=("path", "date"), name="codex_tracking_pageview_path_date_uniq"),
        ),
    ]
