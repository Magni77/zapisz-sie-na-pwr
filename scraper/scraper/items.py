# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy_djangoitem import DjangoItem
from courses.models import Course

import scrapy


class Course(DjangoItem):
    django_model = Course



# class Course(scrapy.Item):
#     groupCode = scrapy.Field()
#     courseCode = scrapy.Field()
#     courseName = scrapy.Field()
#     seatsAmount = scrapy.Field()
#     teacher = scrapy.Field()
#     courseType = scrapy.Field()
#     date = scrapy.Field()
#     last_updated = scrapy.Field(serializer=str)
