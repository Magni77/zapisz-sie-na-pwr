# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from courses.models import Course

class ScraperPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        try:
            course_obj = Course.objects.get(groupCode=item['groupCode'])
            print('Course already in base')
            course_obj.seatsAmount = item['seatsAmount']
            course_obj.teacher = item['teacher']
            course_obj.date = item['date']
            course_obj.room = item['room']
            course_obj.building = item['building']
            course_obj.save()
            return item
        except Course.DoesNotExist:
            pass

        item.save()
        return item
