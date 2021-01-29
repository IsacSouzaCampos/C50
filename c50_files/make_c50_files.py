import numpy as np
import math
import os


class MakeC50Files:
	@staticmethod
	def save_names_file(nfeat, filename):
		try:
			f = open(filename, 'w')
			print('Fout.\n', file=f)
			for _i in range(nfeat):
				print('X%d:\t0,1.' % _i, file=f)

			print('Fout:\t0,1.', file=f)
			f.close()

			print(f'{filename.split(".")[0].split("/")[-1]} C5.0 INPUT FILES CREATED')

		except Exception as e:
			raise e

	@staticmethod
	def is_balanced(full_path):
		from shutil import copyfile
		copyfile(full_path, full_path.replace('.pla', '_temp.pla'))

		number_of_0 = 0
		number_of_1 = 0

		if '.pla' in full_path and '_out_' in full_path:
			with open(full_path, 'r') as fin:
				for line in fin.readlines():
					if line[0] == '0' or line[0] == '1':
						if line[-2] == '0':
							number_of_0 += 1
						else:
							number_of_1 += 1
			# print(f'{_path}:\nnumber of 0\'s = {number_of_0}\nnumber of 1\'s = {number_of_1}\n=============')
		# math.fabs(number_of_0 - number_of_1) < max(number_of_0, number_of_1) / 10, number_of_0
		return max(number_of_0, number_of_1) / (number_of_0 + number_of_1), number_of_0

	@staticmethod
	def disbalance(full_path, number_of_0):
		final_table = ''

		number_of_removals = math.floor(number_of_0 / 10)
		number_of_removals -= number_of_removals % 64
		if number_of_removals < 64:
			number_of_removals = 64

		with open(full_path, 'r') as fin:
			for line in fin.readlines():
				if line[0] == '0' or line[0] == '1':
					if line[-2] == '0' and number_of_removals > 0:
						number_of_removals -= 1
					else:
						final_table += line
				else:
					final_table += line

		with open(full_path, 'w') as fout:
			print(final_table[:-1], file=fout)

	def run_make_files(self, base_name):
		errors = []
		output_proportion = float()

		try:
			output_proportion, number_of_0 = self.is_balanced('temp/' + base_name + '.pla')

			if output_proportion < 0.6:
				print(base_name + '_temp.pla DISBALANCED')
				self.disbalance('temp/' + base_name + '_temp.pla', number_of_0)

			c50f_data_final_name = base_name + '_temp.data'
			c50f_names_final_name = base_name + '_temp.names'
			c50f_test_final_name = base_name + '_temp.test'

			ftrain = open(f'temp/{base_name}' + '_temp.pla', 'r')
			ftest = open(f'temp/{base_name}' + '_temp.pla', 'r')

			lines = ftrain.readlines()
			lines_test = ftest.readlines()
			ftrain.close()
			ftest.close()

			train_data = []
			test_data = []
			for line in lines:
				if '.' in line or '#' in line:
					continue
				x, y = line.split()
				x = [_ for _ in x]
				train_data.append(x+[y])

			for line in lines_test:
				if '.' in line or '#' in line:
					continue
				x, y = line.split()
				x = [_ for _ in x]
				test_data.append(x+[y])

			train_data = np.array(train_data)
			test_data = np.array(test_data)
			np.savetxt('c50_files/files/' + c50f_data_final_name, train_data, fmt='%c', delimiter=',')
			np.savetxt('c50_files/files/' + c50f_test_final_name, test_data, fmt='%c', delimiter=',')
			self.save_names_file(nfeat=train_data.shape[1]-1, filename='c50_files/files/' + c50f_names_final_name)

		except Exception as e:
			errors.append((base_name, e))

		return errors, output_proportion
