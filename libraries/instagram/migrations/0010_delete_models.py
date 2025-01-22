from django.db import migrations


class Migration(migrations.Migration):
    dependencies: list[tuple[str, str]] = [
        ("instagram", "0002_ig-oauth"),
        ("instagram", "0008_igsettings"),
        ("instagram", "0009_ig_a11y_json"),
    ]

    operations = [
        migrations.DeleteModel(name="InstagramSettings"),
        migrations.DeleteModel(name="InstagramOAuthToken"),
    ]
