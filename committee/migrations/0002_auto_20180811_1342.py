# Generated by Django 2.0.8 on 2018-08-11 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('committee', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='abbrev',
            field=models.CharField(blank=True, help_text='A really short abbreviation for the committee. Has no special significance.', max_length=255),
        ),
        migrations.AlterField(
            model_name='committee',
            name='code',
            field=models.CharField(db_index=True, help_text='An alphanumeric code used for the committee on THOMAS.gov, House.gov, and Senate.gov.', max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='committee',
            name='committee',
            field=models.ForeignKey(blank=True, help_text='This field indicates whether the object is a commmittee, in which case the committee field is null, or a subcommittee, in which case this field gives the parent committee.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subcommittees', to='committee.Committee'),
        ),
        migrations.AlterField(
            model_name='committee',
            name='committee_type',
            field=models.IntegerField(blank=True, choices=[(1, 'Senate'), (3, 'House'), (2, 'Joint')], help_text='Whether this is a House, Senate, or Joint committee.', null=True),
        ),
        migrations.AlterField(
            model_name='committee',
            name='jurisdiction',
            field=models.TextField(blank=True, help_text="The committee's jurisdiction, if known.", null=True),
        ),
        migrations.AlterField(
            model_name='committee',
            name='jurisdiction_link',
            field=models.TextField(blank=True, help_text='A link to where the jurisdiction text was sourced from.', null=True),
        ),
        migrations.AlterField(
            model_name='committee',
            name='name',
            field=models.CharField(help_text="The name of the committee or subcommittee. Committee names typically look like '{House,Senate} Committee on ...', while subcommmittee names look like 'Legislative Branch'.", max_length=255),
        ),
        migrations.AlterField(
            model_name='committee',
            name='obsolete',
            field=models.BooleanField(db_index=True, default=False, help_text='True if this committee no longer exists.'),
        ),
        migrations.AlterField(
            model_name='committee',
            name='url',
            field=models.CharField(blank=True, help_text="The committee's website.", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='committeemeeting',
            name='committee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='meetings', to='committee.Committee'),
        ),
        migrations.AlterField(
            model_name='committeemember',
            name='committee',
            field=models.ForeignKey(help_text='The committee or subcommittee being served on.', on_delete=django.db.models.deletion.PROTECT, related_name='members', to='committee.Committee'),
        ),
        migrations.AlterField(
            model_name='committeemember',
            name='person',
            field=models.ForeignKey(help_text='The Member of Congress serving on a committee.', on_delete=django.db.models.deletion.CASCADE, related_name='committeeassignments', to='person.Person'),
        ),
        migrations.AlterField(
            model_name='committeemember',
            name='role',
            field=models.IntegerField(choices=[(2, 'Chair'), (3, 'Ranking Member'), (5, 'Member'), (4, 'Vice Chair'), (1, 'Ex Officio')], default=5, help_text='The role of the member on the committee.'),
        ),
    ]