from django.contrib import admin

from shared import file_loader

class FilePreprocessorAdmin(admin.ModelAdmin):
	# TODO refactor for one set
	# depending on framework selection forward to the submodel
	def response_add(self, request, obj, post_url_continue=None):

		if obj.input_file_format == 'parquet':
			print('Allow every format, time series')
			save_parquet_file(obj)
		elif obj.input_file_format == 'wav':
			print('to numpy, classification or binary')
		elif obj.input_file_format == 'png':
			print('to numpy using klaidi, classification or binary')

		# TODO this is the fileformat changer
		# TODO Add additional task changer

	def has_change_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False


def save_parquet_file(obj):
	feature_data, labels_data = file_loader(obj.input_file_name, obj.labels_file_name)

	names = []
	for name in [obj.input_file_name, obj.labels_file_name]:
		if name.split('.'):
			name = name.rsplit(' ', 1)[0]
			names.append(name)

	for name in names:
		if obj.output_file_format == 'csv':
			feature_data.to_csv(name + '.csv')
		elif obj.output_file_format == 'npy':
			feature_data.as_matrix(name + '.npy')
		elif obj.output_file_format == 'pkl':
			feature_data.to_pickle(name + '.pkl')
