from django.db import models
import datetime

class History_Table(models.Model):
	id = models.AutoField(primary_key=True)
	history_id = models.IntegerField(default=0)
	history_type = models.CharField(max_length=6)
	history_updated = models.DateTimeField(default=datetime.date.today)

	class Meta:
		abstract = True
		get_latest_by = 'history_id'

class Model_History(models.Model):
	def __init__(self, *args, **kwargs):
		super(Model_History, self).__init__(*args, **kwargs)
		class Meta:
			pass
		setattr(Meta, 'app_label', 'history')
		setattr(Meta, 'get_latest_by', 'id')
		attrs = self.get_fields()
		attrs.update({
			'Meta': Meta, 
			'__module__': 'history.models'
		})
		self.history = type(self._meta.object_name+"_History", (History_Table,), attrs)

	def get_fields(self):
		attrs = {}
		for field in self._meta.fields:
			if isinstance(field, (
					models.DateField, 
					models.DateTimeField, 
					models.CharField,
					models.IntegerField )):
				attrs.update({field.name: field})
		return attrs

	def save(self, *args, **kwargs):
		history_type = 'insert'
		if self.pk:
		 	if self.__class__.objects.get(pk=self.id):
		 		history_type = 'update'
		super(Model_History, self).save(*args, **kwargs)
		history_dict = {
			'id': None,
			'history_id': self.id,
			'history_type': history_type,
		}
		for field in self.history._meta.fields:
			if field.name in self.__dict__ and field.name != 'id':
				history_dict[field.name] = self.__dict__[field.name]
		self.history.objects.create(**history_dict)

	def delete(self, *args, **kwargs):
		"""
			Removes an instance from database table and insert changes in 
			history class
		"""
		history_dict = {
			'id': None,
			'history_id': self.id,
			'history_type': 'delete',
		}
		self.history.objects.create(**history_dict)
		super(Model_History, self).delete(*args, **kwargs)

	class Meta:
		abstract = True
		get_latest_by = 'pk'

class Model_Sample(Model_History):
	title = models.CharField(max_length=100)

	def __unicode__(self):
		if self.pk and self.title:
			return u'pk: %s - title: %s' % (self.pk, self.title)
		else:
			return 'void Model_Sample'

sample_instance = Model_Sample()