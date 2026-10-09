from django.db import migrations


def create_placement_incharge_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Placement Incharge')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            create_placement_incharge_group,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
