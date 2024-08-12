import time
from random import sample

from bson import ObjectId
from flask import Blueprint, request, jsonify

from app.models.encounter import Encounter
from app.models.item import Item
from app.models.rolltable import RollTable
from app.models.room import Room

roll_bp = Blueprint('roll_bp', __name__)


@roll_bp.route('/', methods=['POST'])
def perform_roll(**kwargs):
    """
    Roll from a specified table and return unique results.
    Request JSON:
    {
        "rolltable_id": "<rolltable_id>",
        "num_results": x,
        "constraints": {"claimed": false}  # Optional
    }
    """
    data = request.get_json()
    rolltable_id = data.get('rolltable_id')
    num_results = data.get('num_results')
    constraints = data.get('constraints', {})

    max_retries = 3
    retry_delay = 0.1  # 100 milliseconds

    try:
        rolltable = RollTable.objects(id=ObjectId(rolltable_id)).first()
        if not rolltable:
            return jsonify({'message': 'RollTable not found!'}), 404

        if rolltable.items:
            entry_model = Item
            entry_ids = rolltable.items
        elif rolltable.encounters:
            entry_model = Encounter
            entry_ids = rolltable.encounters
        elif rolltable.rooms:
            entry_model = Room
            entry_ids = rolltable.rooms
        else:
            return '', 204

        filter_criteria = {k: v for k, v in constraints.items()}
        filter_criteria['_id'] = {'$in': [entry.id for entry in entry_ids]}
        if entry_model == Item:
            filter_criteria['available'] = True
        filtered_entries = list(entry_model.objects(__raw__=filter_criteria))

        if not filtered_entries:
            return '', 204

        min(num_results, len(filtered_entries))

        selected_results = []
        attempts = 0

        while len(selected_results) < num_results and attempts < max_retries:
            remaining_needed = num_results - len(selected_results)
            sample_size = min(remaining_needed, len(filtered_entries))

            selected_entries = sample(filtered_entries, sample_size)

            for entry in selected_entries:
                if entry_model == Item:
                    updated_entry = Item.objects(id=entry.id, available=True).modify(set__available=False)
                    if updated_entry:
                        selected_results.append(updated_entry)
                        filtered_entries.remove(entry)
                else:
                    selected_results.append(entry)

            # Increment retry count and wait before retrying if needed
            if len(selected_results) < num_results:
                attempts += 1
                time.sleep(retry_delay)

        # If we can't get enough available items, return what we have
        if selected_results:
            results = [result.to_mongo().to_dict() for result in selected_results]
            return jsonify({'results': results}), 200
        else:
            return '', 204  # No items were successfully acquired

    except Exception as e:
        return jsonify({'message': str(e)}), 500
