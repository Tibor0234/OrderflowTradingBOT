from session_pairs.resource import Resource
from data_managers.news.subscriber import NewsManagerSubscriber
from data_managers.news.utils import NewsMessage

class NewsAnalyzer(Resource, NewsManagerSubscriber):
    def __init__(self):
        pass

    def process_message(self, msg: NewsMessage):
        pass