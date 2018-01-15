import logging
from typing import List

from django.core.exceptions import ObjectDoesNotExist

from turns.models import IntentTemplate, SlotTemplate, SlotType

logger = logging.getLogger('turns')


def persist_intent_template(intent_template: dict):
    dialog_flow_id = intent_template['id']
    name = intent_template['name']
    obj, created = IntentTemplate.objects.get_or_create(dialog_flow_id=dialog_flow_id)
    obj.name = name
    obj.save()

    slots_created = persist_slot_templates(intent_template['parameters'], obj)

    return created, slots_created


def persist_intent_templates(intent_templates: List[dict]):
    total_intents_created = 0
    total_slots_created = 0
    for intent_template in intent_templates:
        created, slots_created = persist_intent_template(intent_template)
        if created:
            total_intents_created += 1
            total_slots_created += slots_created
    logger.info(
        'Persisted {} new intents with a total of {} new slots.'.format(total_intents_created, total_slots_created))
    return total_intents_created, total_slots_created


def persist_slot_template(slot_template: dict, intent_template: IntentTemplate):
    dialog_flow_id = slot_template['id']
    data_type = slot_template['dataType']
    name = slot_template['name']
    value = slot_template['value']
    is_list = bool(slot_template['isList'])

    data_type, _ = SlotType.objects.get_or_create(name=data_type)

    try:
        obj = SlotTemplate.objects.get(dialog_flow_id=dialog_flow_id)
        created = False
    except ObjectDoesNotExist:
        created = True
        obj = SlotTemplate.objects.create(dialog_flow_id=dialog_flow_id,
                                          intent_template=intent_template,
                                          type=data_type)
    obj.type = data_type
    obj.name = name
    obj.value = value
    obj.is_list = is_list
    obj.intent_template = intent_template
    obj.save()

    return obj, created


def persist_slot_templates(slot_templates: List[dict], intent_template):
    total_created = 0
    for slot_template in slot_templates:
        _, created = persist_slot_template(slot_template, intent_template)
        if created:
            total_created += 1
    return total_created
