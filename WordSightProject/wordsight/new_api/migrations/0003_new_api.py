# Generated by Django 4.2 on 2023-05-02 06:37
import json
import re
from datetime import datetime
from django.db import migrations
from django.core.management import call_command

def load_file(apps, schema_editor):
    News_model = apps.get_model("new_api", "News")
    with open("new_api\example.json", encoding='UTF8') as json_file:
        data = json.load(json_file)
        for elem in data:
            tag_split = re.split(r'\s+', re.sub(r'[,\-!?>|]', ' ', elem["tag"]))
            # 기자 이름 필터링 필요. 예) 기자이름|기자| -> 기자이름
            # 스트링 공백제거 필요
            news_model = News_model.objects.create(
                title = elem["title"],
                reporter = elem["reporter"],
                news_agency = elem["news_agency"],
                origin_address = elem["origin_url"],
                created_date = datetime.strptime(elem["created_date"], "%Y-%m-%d").date(),
                news_content = elem["news_contents"],
                image_link = elem["image"],
                tag = ",".join(set(tag_split))
            )

class Migration(migrations.Migration):

    dependencies = [
        ('new_api', '0002_alter_news_news_content'),
    ]

    operations = [
        migrations.RunPython(load_file, None)
    ]
