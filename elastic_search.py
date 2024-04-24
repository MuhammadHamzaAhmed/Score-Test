import sys
import traceback

from elasticsearch import Elasticsearch

INDEX_NAME = "search-resumes-dev"
ELASTIC_HOST = "https://elastic.3cix.com/"
ELASTIC_USERNAME = "elastic"
ELASTIC_PASSWORD = "pK1k8c3RiBYxq943GY43e1U2"

index_settings = {"settings": {"number_of_shards": 1, "number_of_replicas": 0}}
client = Elasticsearch(ELASTIC_HOST, http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD), verify_certs=True, timeout=50)


def save_document_in_elastic_search(document_body):
    try:
        client.index(index=INDEX_NAME, body=document_body)
    except Exception as e:
        print("Unable to connect to Elasticsearch server:", e, file=sys.stderr)


def save_document_in_es(document_body, index_name):
    try:
        client.index(index=index_name, body=document_body)
    except Exception as e:
        print("Unable to connect to Elasticsearch server:", e, file=sys.stderr)


def document_exists_in_es(unique_identifier, index_name):
    try:
        result = client.search(index=index_name,
                               body={"query": {"match": {"payload.UniqueIdentifier.keyword": unique_identifier}}})
        return result['hits']['total']['value'] > 0
    except Exception as e:
        print("Error while checking document existence in Elasticsearch:", e, file=sys.stderr)
        return False


def delete_index(index_name):
    try:
        if client.indices.exists(index=index_name):
            client.indices.delete(index=index_name)
            print("Index '{}' deleted successfully.".format(index_name))
        else:
            print("Index '{}' does not exist.".format(index_name))
    except Exception as e:
        print("Error deleting index '{}':".format(index_name), e, file=sys.stderr)


def get_resumes(applicant_id):
    query_body = {"size": 1, "query": {"bool": {"must": {"match": {"uniqueIdentifier.keyword": applicant_id}}}}}
    try:
        req = client.search(index=INDEX_NAME, body=query_body)['hits']['hits'][0]['_source']
        return req
    except:
        traceback.print_exc()
