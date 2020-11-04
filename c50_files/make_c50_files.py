import numpy as np
import os


class MakeC50Files:
	@staticmethod
	def save_names_file(nfeat, filename):
		print(filename)
		f = open(filename, 'w')
		print('Fout.\n', file=f)
		for _i in range(nfeat):
			print('X%d:\t0,1.' % _i, file=f)

		print('Fout:\t0,1.', file=f)
		f.close()

	@staticmethod
	def split_outputs(_path):
		with open(f'Benchmarks/{_path}', 'r') as fin:
			for line in fin.readlines():
				if '.i' in line:
					if int(line.split(' ')[1]) > 16:
						raise Exception('Numero de inputs superior a 16')
					else:
						break
		with open('temp/collapse_script', 'w') as fout:
			print('read_pla Benchmarks/'+_path+'; collapse; write_pla -m temp/temp.pla', file=fout)
		os.system('./abc -F temp/collapse_script')

		number_of_outputs = 0
		with open('temp/temp.pla', 'r') as fin:
			temp_pla = fin.read()
			for _line in temp_pla.splitlines():
				if '.o' in _line:
					number_of_outputs = int(_line.split()[1])
					break

		for _i in range(number_of_outputs):
			with open('temp/temp_out_'+str(_i)+'.pla', 'w') as fout:
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

	def run_make_files(self):
		output_csv = open('c50_results.csv', 'w')
		print(','.join(['base_name', 'sk_acc_tree', 'sk_acc_rf', 'tr_acc', 'te_acc', 'eq_one', 'eq_zero']),
				file=output_csv)

		for path in os.listdir('Benchmarks'):
			if '.pla' not in path:
				continue
			print(path)

			try:
				for i in range(self.split_outputs(path)):
					file_name = path.split('.')[0]
					base_name = 'temp/temp_out_'+str(i)

					c50f_data_final_name = file_name + '_out_' + str(i) + '.data'
					c50f_names_final_name = file_name + '_out_' + str(i) + '.names'
					c50f_test_final_name = file_name + '_out_' + str(i) + '.test'

					ftrain = open('temp/temp_out_'+str(i)+'.pla', 'r')
					ftest = open('temp/temp_out_'+str(i)+'.pla', 'r')

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
				print(e)
		output_csv.close()
