from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

class ElasticsearchTool:
    def __init__(self, ):
        es_host = "http://43.142.151.181:9200"

        # 用户名和密码
        username = "elastic"
        password = "MBDcbneAh1OmE53IkwzL"

        # 使用用户名和密码连接到 Elasticsearch
        client = Elasticsearch(es_host, basic_auth=(username, password))
        self.es = client
    def get_document(self, index_name, doc_id):
        """ 获取文档 """
        indexInfo=self.es.get(index=index_name, id=doc_id)
        return indexInfo.raw.get("_source");

    def insert_document(self, index_name,doc_id, document):
        # 索引文档
        response = self.es.index(index=index_name,  id=doc_id, body=document)
        return response

    def update_document(self, index_name, doc_id, update_body):
        """ 更新文档 """
        return self.es.update(index=index_name, id=doc_id, body={"doc": update_body})

    def bulk_index_documents(self, index_name, documents):
        """ 批量索引文档 """
        actions = [
            {"_index": index_name, "_id": doc.get('id', None), "_source": doc}
            for doc in documents
        ]
        return bulk(self.es, actions)

    def search_documents(self, index_name, query):
        page_size = 100
        page = 0
        results = []

        while True:
            response = self.es.search(index=index_name, query=query, from_=page * page_size, size=page_size)
            hits = response['hits']['hits']
            if not hits:
                break
            hitArr = [d["_source"] for d in hits]
            results.extend(hitArr)
            page += 1

        return results


    #获取样例数据
    def get_example_data(self, ):
        es = ElasticsearchTool()
        return es.search_documents(index_name="day_k_line", query={
            "match": {
                "code": "603220"
            }
        })

    def get_kline_data(self, code):
        es = ElasticsearchTool()
        return es.search_documents(index_name="day_k_line", query={
            "match": {
                "code": code
            }
        })