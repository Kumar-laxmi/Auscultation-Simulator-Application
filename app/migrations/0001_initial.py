# Generated by Django 4.2.9 on 2024-01-11 06:48

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='heartAudio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sound_name', models.CharField(choices=[('acute_myocardial_infection', 'Acute Myocardial Infection'), ('acute_pericarditis', 'Acute Pericarditis'), ('aortic_stenosis_and_regurgitation', 'Aortic Stenosis and Regurgitation'), ('aortic_valve_regurgitation', 'Aortic Valve Regurgitation'), ('aortic_valve_stenosis', 'Aortic Valve Stenosis'), ('atrial_septal_defect', 'Atrial Septal Defect'), ('austin_flint_murmur', 'Austin Flint Murmur'), ('coarctation_of_the_aorta', 'Coarctation of the Aorta'), ('congenital_aortic_stenosis', 'Congenital Aortic Stenosis'), ('congestive_heart_failure', 'Congestive Heart Failure'), ('continuous_murmur', 'Continuous Murmur'), ('diastolic_murmur', 'Diastolic Murmur'), ('dilated_cardiomyopathy', 'Dilated Cardiomyopathy'), ('early_systolic_murmur', 'Early Systolic Murmur'), ('ebsteins_anomaly', 'Ebsteins Anomaly'), ('fourth_heart_sound_gallop', 'Fourth Heart Sound Gallop'), ('functional_murmur', 'Functional Murmur'), ('holosystolic_murmur', 'Holosystolic Murmur'), ('hypertrophic_cardiomyopathy', 'Hypertrophic Cardiomyopathy'), ('mid-systolic_murmur', 'Mid-systolic Murmur'), ('mitral_stenosis_and_regurgitation', 'Mitral Stenosis and Regurgitation'), ('mitral_stenosis_and_tricuspid_regurgitation', 'Mitral Stenosis and Tricuspid Regurgitation'), ('mitral_valve_prolapse', 'Mitral Valve Prolapse'), ('mitral_valve_regurgitation', 'Mitral Valve Regurgitation'), ('mitral_valve_stenosis', 'Mitral Valve Stenosis'), ('normal_heart', 'Normal Heart'), ('opening_snap', 'Opening Snap'), ('patent_ductus_arteriosus', 'Patent Ductus Arteriosus'), ('pericardial_rub', 'Pericardial Rub'), ('pulmonary_hypertension', 'Pulmonary Hypertension'), ('pulmonary_valve_regurgitation', 'Pulmonary Valve Regurgitation'), ('pulmonary_valve_stenosis', 'Pulmonary Valve Stenosis'), ('split_first_heart_sound', 'Split First Heart Sound'), ('split_second_heart_sound', 'Split Second Heart Sound'), ('stills_murmur', 'Stills Murmur'), ('systemic_hypertension', 'Systemic Hypertension'), ('tetralogy_of_fallot', 'Tetralogy of Fallot'), ('third_heart_sound_gallop', 'Third Heart Sound Gallop'), ('tricuspid_valve_regurgitation', 'Tricuspid Valve Regurgitation'), ('ventricular_aneurysm', 'Ventricular Aneurysm'), ('ventricular_septal_defect', 'Ventricular Septal Defect')], max_length=50)),
                ('sound_type', models.CharField(choices=[('A', 'Type A'), ('E', 'Type E'), ('M', 'Type M'), ('P', 'Type P'), ('T', 'Type T')], max_length=1)),
                ('audio_file', models.FileField(storage=app.models.OverwriteStorage(), upload_to='app/static/audio/heart/<django.db.models.fields.CharField>/<django.db.models.fields.CharField>/')),
            ],
        ),
    ]
