from flask import jsonify
from bson import ObjectId
from mongoengine import Document

def dereference_object_id(object_dict):
    object_dict["_id"] = str(object_dict["_id"])
    return object_dict
    

def get_document(document_class, doc_id):
    try:
        document = document_class.objects(id=ObjectId(doc_id)).first()
        if not document:
            return jsonify({'message': f'{document_class.__name__} not found!'}), 404
        return document
    except Exception as e:
        return jsonify({'message': str(e)}), 400

def create_document(document_class, data):
    try:
        document = document_class(**data)
        document.save()
        return jsonify(dereference_object_id(document.to_mongo().to_dict())), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

def update_document(document, data):
    try:
        document.update(**data)
        document.reload()  # Reload to get updated document
        return jsonify(dereference_object_id(document.to_mongo().to_dict())), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

def delete_document(document):
    try:
        document.delete()
        return jsonify({'message': f'{document.__class__.__name__} deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

def get_all_documents(document_class):
    try:
        documents = document_class.objects()
        return jsonify([dereference_object_id(doc.to_mongo().to_dict()) for doc in documents]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400
