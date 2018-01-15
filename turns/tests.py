from django.db import IntegrityError
from django.test import TestCase

from turns.models import IntentTemplate, SlotTemplate, SlotType


class IntentTemplateTests(TestCase):
    def setUp(self):
        IntentTemplate.objects.create(dialog_flow_id='abc', name='intent_1_template')
        IntentTemplate.objects.create(dialog_flow_id='def', name='intent_2_template')

    def test_creation(self):
        assert len(IntentTemplate.objects.all()) == 2

    def test_dialog_flow_id_unique(self):
        with self.assertRaises(IntegrityError):
            IntentTemplate.objects.create(dialog_flow_id='abc', name='test_dialog_flow_id_unique')

    def test_name_not_null(self):
        with self.assertRaises(IntegrityError):
            IntentTemplate.objects.create(dialog_flow_id='test_name_not_null', name=None)

    def test_dialog_flow_id_not_null(self):
        with self.assertRaises(IntegrityError):
            IntentTemplate.objects.create(dialog_flow_id=None, name='test_dialog_flow_id_not_null')

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            IntentTemplate.objects.create(dialog_flow_id='test_name_unique', name='intent_1_template')


class SlotTypeTest(TestCase):
    def setUp(self):
        SlotType.objects.create(name='type_1')
        SlotType.objects.create(name='type_2')

    def test_creation(self):
        assert len(SlotType.objects.all()) == 2

    def test_name_not_null(self):
        with self.assertRaises(IntegrityError):
            SlotType.objects.create(name=None)

    def test_name_unique(self):
        with self.assertRaises(IntegrityError):
            SlotType.objects.create(name='type_1')


class SlotTemplateTests(TestCase):
    def setUp(self):
        self.intent_template = IntentTemplate.objects.create(dialog_flow_id='abc', name='intent_template')
        self.type = SlotType.objects.create(name='type')
        SlotTemplate.objects.create(dialog_flow_id='abc',
                                    name='slot_1_template',
                                    type=self.type,
                                    value='$value',
                                    intent_template=self.intent_template)
        SlotTemplate.objects.create(dialog_flow_id='def',
                                    name='slot_2_template',
                                    type=self.type,
                                    value='$value',
                                    intent_template=self.intent_template)

    def test_creation(self):
        assert len(SlotTemplate.objects.all()) == 2

    def test_dialog_flow_id_unique(self):
        with self.assertRaises(IntegrityError):
            SlotTemplate.objects.create(dialog_flow_id='abc',
                                        name='test_dialog_flow_id_unique',
                                        value='$value',
                                        type=self.type,
                                        intent_template=self.intent_template)

    def test_name_not_null(self):
        with self.assertRaises(IntegrityError):
            SlotTemplate.objects.create(dialog_flow_id='test_name_not_null',
                                        value='$value',
                                        name=None,
                                        type=self.type,
                                        intent_template=self.intent_template)

    def test_dialog_flow_id_not_null(self):
        with self.assertRaises(IntegrityError):
            SlotTemplate.objects.create(dialog_flow_id=None,
                                        name='test_dialog_flow_id_not_null',
                                        value='$value',
                                        type=self.type,
                                        intent_template=self.intent_template)

    def test_name_not_unique(self):
        try:
            SlotTemplate.objects.create(dialog_flow_id='test_name_not_unique',
                                        name='slot_1_template',
                                        value='$value',
                                        type=self.type,
                                        intent_template=self.intent_template)
        except IntegrityError:
            self.fail('SlotTemplate.name has unique constraint. Musn\'t have this!')
        else:
            pass

    def test_value_not_null(self):
        with self.assertRaises(IntegrityError):
            SlotTemplate.objects.create(dialog_flow_id='value_not_null',
                                        name='value_not_null',
                                        value=None,
                                        type=self.type,
                                        intent_template=self.intent_template)

    def test_is_list_default(self):
        obj = SlotTemplate.objects.create(dialog_flow_id='is_list_default',
                                          name='is_list_default',
                                          value='$value',
                                          type=self.type,
                                          intent_template=self.intent_template)
        assert not obj.is_list

    def test_type_not_null(self):
        with self.assertRaises(IntegrityError):
            SlotTemplate.objects.create(dialog_flow_id='value_not_null',
                                        name='value_not_null',
                                        value=None,
                                        intent_template=self.intent_template)

    def test_intent_template_not_null(self):
        with self.assertRaises(IntegrityError):
            SlotTemplate.objects.create(dialog_flow_id='value_not_null',
                                        name='value_not_null',
                                        value=None,
                                        type=self.type)
