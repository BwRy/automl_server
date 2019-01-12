import datetime
import os
import pickle
import time

import autokeras as ak
import numpy
from autokeras import ImageClassifier

from automl_server.settings import AUTO_ML_MODELS_PATH, AUTO_ML_DATA_PATH
from automl_systems.shared import load_training_data
from training_server.celery import app
from training_server.models.auto_keras_config import AutoKerasConfig

@app.task()
def train(auto_keras_config_id):
	print('auto_keras_config_object: ' + str(auto_keras_config_id))
	auto_keras_config = AutoKerasConfig.objects.get(id=auto_keras_config_id)

	auto_keras_config.status = 'in_progress'
	auto_keras_config.save()
	# Storing save location for models

	try:
		dump_file = os.path.join(AUTO_ML_MODELS_PATH, 'auto_keras' + str(datetime.datetime.now()) + '.dump')

		x, y = load_training_data(auto_keras_config.input_data_filename, auto_keras_config.labels_filename, False)

		clf = ImageClassifier(verbose=auto_keras_config.verbose)

		start = time.time()
		clf.fit(x, y, time_limit=auto_keras_config.time_limit)
		end = time.time()

		#clf.final_fit(x_train, y_train, x_test, y_test, retrain=True)
		#y = clf.evaluate(x_test, y_test)

		print("Fitting Success!!!")

		print(dump_file)
		# storing the best performer
		clf.export_autokeras_model('auto_keras_v1.h5')
		print('after export')

		from keras.models import load_model
		from keras.utils import plot_model
		plot_model(clf, to_file='my_model.png')

		auto_keras_config.training_time = round(end-start, 2)
		auto_keras_config.status = 'success'
		auto_keras_config.model_path = dump_file
		auto_keras_config.save()
		print('Status final ' + auto_keras_config.status)

	except Exception as e:
		end = time.time()
		if 'start' in locals():
			print('failed after:' + str(end-start))
			auto_keras_config.training_time = round(end-start, 2)

		auto_keras_config.status = 'fail'
		auto_keras_config.additional_remarks = e
		auto_keras_config.save()