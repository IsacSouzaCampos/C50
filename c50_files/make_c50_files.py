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
	def split_outputs(_path):
		try:
			with open(f'Benchmarks/{_path}', 'r') as fin:
				for line in fin.readlines():
					if '.i' in line:
						if int(line.split(' ')[1]) > 16:
							raise Exception('Numero de inputs superior a 16')
						else:
							break
			with open('temp/collapse_script', 'w') as fout:
				print('read_pla Benchmarks/' + _path + f'; collapse; write_pla -m temp/{_path}', file=fout)
			os.system('./abc -F temp/collapse_script')

			number_of_outputs = 0
			with open(f'temp/{_path}', 'r') as fin:
				temp_pla = fin.read()
				for _line in temp_pla.splitlines():
					if '.o' in _line:
						number_of_outputs = int(_line.split()[1])
						break

			for _i in range(number_of_outputs):
				with open(f'temp/{_path.replace(".pla", "")}_out_'+str(_i)+'.pla', 'w') as fout:
					for _line in temp_pla.splitlines():
						if _line[0] not in ['0', '1']:
							if '#' in _line or '.e' in _line:
								continue
							print(_line, file=fout)
						else:
							_lines = _line.split()
							print(_lines[0]+' '+_lines[1][_i], file=fout)
					print('.e', file=fout)

			return number_of_outputs

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
		return math.fabs(number_of_0 - number_of_1) < max(number_of_0, number_of_1)/10, number_of_0

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

		with open(full_path.replace('.pla', '_temp.pla'), 'w') as fout:
			print(final_table[:-1], file=fout)

	def run_make_files(self, path):
		errors = []
		number_of_outputs = 0

		try:
			base_name = path.replace('.pla', '')
			number_of_outputs = self.split_outputs(path)

			for i in range(number_of_outputs):
				is_balanced, number_of_0 = self.is_balanced('temp/' + base_name + '_out_' + str(i) + '.pla')
				if is_balanced:
					self.disbalance('temp/' + base_name + '_out_' + str(i) + '.pla', number_of_0)

				c50f_data_final_name = base_name + '_out_' + str(i) + '_temp.data'
				c50f_names_final_name = base_name + '_out_' + str(i) + '_temp.names'
				c50f_test_final_name = base_name + '_out_' + str(i) + '_temp.test'

				ftrain = open(f'temp/{base_name}_out_'+str(i)+'_temp.pla', 'r')
				ftest = open(f'temp/{base_name}_out_'+str(i)+'_temp.pla', 'r')

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
				np.savetxt('c50_files/files/'+c50f_data_final_name, train_data, fmt='%c', delimiter=',')
				np.savetxt('c50_files/files/'+c50f_test_final_name, test_data, fmt='%c', delimiter=',')
				self.save_names_file(nfeat=train_data.shape[1]-1, filename='c50_files/files/'+c50f_names_final_name)

		except Exception as e:
			errors.append((path, e))

		return errors, number_of_outputs
