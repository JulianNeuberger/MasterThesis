import logging
from typing import List

from turns.models import IntentTemplate, ParameterTemplate

logger = logging.getLogger('turns')


def persist_intent_template(intent_template: dict):
    dialog_flow_id = intent_template['id']
    name = intent_template['name']
    obj, created = IntentTemplate.objects.get_or_create(dialog_flow_id=dialog_flow_id)
    obj.name = name
    parameters_created = 0
    try:
        for raw_parameter in intent_template['parameters']:
            parameter_name = raw_parameter['name']
            try:
                logger.debug('Adding expected parameter "{}" to intent "{}"'.format(
                    parameter_name,
                    obj.name
                ))
                parameter_template, created = ParameterTemplate.objects.get_or_create(name=parameter_name)
                parameter_template.save()
                obj.parameters.add(parameter_template)
                parameters_created += 1 if created else 0
            except KeyError:
                # parameter not given
                logger.info('Intent template "{}" expects parameter "{}", but didn\'t get it!'.format(
                    obj.name,
                    parameter_name
                ))
                continue
    except KeyError:
        # no parameters expected
        pass

    obj.save()
    return created, parameters_created


def persist_intent_templates(intent_templates: List[dict]):
    total_intents_created = 0
    total_parameters_created = 0
    for intent_template in intent_templates:
        created, parameters_created = persist_intent_template(intent_template)
        if created:
            total_intents_created += 1
        total_parameters_created += parameters_created
    logger.info(
        'Persisted {} new intents with a total of {} new parameters.'.format(total_intents_created,
                                                                             total_parameters_created))
    return total_intents_created, total_parameters_created


def persist_parameter_template(parameter_template: dict):
    name = parameter_template['name']

    obj, created = ParameterTemplate.objects.get_or_create(name=name)
    obj.is_list = parameter_template['isList']
    obj.save()

    return obj, created


def persist_parameter_templates(parameter_templates: List[dict]):
    total_created = 0
    for parameter_template in parameter_templates:
        _, created = persist_parameter_template(parameter_template)
        if created:
            total_created += 1
    return total_created
