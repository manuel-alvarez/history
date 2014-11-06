from django.db import models
from django.test import TestCase

from history.models import Model_Sample, Model_History, History_Table

class HistoryTests(TestCase):
	"""
		Run Tests
	"""
	def check_history_instance(self, instance, saved_as='insert'):
		self.assertIsInstance(instance, Model_History)

		print 'Record must be saved as %s in history table' % saved_as
		history_instance = instance.history.objects.latest()
		self.assertIsInstance(history_instance, History_Table)
		self.assertEqual(history_instance.history_type, saved_as)
		print '	', history_instance

		print 'Fields must be the same in both tables'
		for field in instance._meta.fields:
			if field.name != 'id':
				self.assertEqual(
					getattr(instance, field.name), 
					getattr(history_instance, field.name)
				)
				print '	%s: %s -> %s' % (
					field.name, 
					getattr(instance, field.name), 
					getattr(history_instance, field.name)
				)

	def test_model_history(self):
		"""
			New model must be instantiated from Model_History and an insert, an 
			update and a delte are made
		"""
		test_instance = Model_Sample()
		test_instance.title = u'this is a title'
		test_instance.save()
		print ''
		print 'INSERT'
		print 'Tables from original model and history model must be the same concatenated with "_history"'
		print '	test_instance._meta.db_table:', test_instance._meta.db_table;
		self.assertEqual(test_instance._meta.db_table + '_history', test_instance.history._meta.db_table)
		print 'Record must be created in main table and object must be instance of Model_History'
		test_instance = Model_Sample.objects.latest()
		print '	', test_instance
		self.check_history_instance(test_instance, 'insert')

		# Update test
		print ''
		print 'UPDATE'
		test_instance = Model_Sample.objects.latest()
		test_instance.title = u'Title changed'
		test_instance.save()
		print 'Record must be created in main table and object must be instance of Model_History'
		print '	', test_instance
		self.check_history_instance(test_instance, 'update')

		# Delete test
		print ''
		print 'DELETE'
		test_instance = Model_Sample.objects.latest()
		test_instance.delete()
		print 'Record must be none'
		self.assertEqual(test_instance.pk, None)
		print '	ok'
		print 'Record must be saved as delete in history table'
		test_history_instance = test_instance.history.objects.latest()
		self.assertIsInstance(test_history_instance, History_Table)
		self.assertEqual(test_history_instance.history_type, 'delete')
		print '	', test_history_instance
