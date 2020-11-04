import numpy as np
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


def get_test_acc_from_dtree(train_data, test_data):
	Xtr, ytr = train_data[:, :-1], train_data[:, -1]
	Xte, yte = test_data[:, :-1], test_data[:, -1]

	tree = DecisionTreeClassifier().fit(Xtr, ytr)
	
	ypred_tree = tree.predict(Xte)

	acc_tree = (ypred_tree == yte).mean()*100

	return str(acc_tree)


def get_train_test_acc_from_random_forest(train_data, test_data):
	Xtr, ytr = train_data[:,:-1], train_data[:,-1]
	Xte, yte = test_data[:,:-1], test_data[:,-1]

	rf = RandomForestClassifier().fit(Xtr, ytr)
	
	ypred_rf = rf.predict(Xte)

	acc_rf = (ypred_rf == yte).mean()*100

	return str(acc_rf)


def parse_output(c50f_output):
	lines = open(c50f_output, 'r').readlines()
	one_equation = []
	zero_equation = []
	for i, line in enumerate(lines):
		if 'Evaluation on training data' in line:
			acc_line_tr = i+6
			acc_tr = lines[acc_line_tr].split('(')[1].split(')')[0].strip('%')
			acc_tr = str(100-float(acc_tr))
		if 'Evaluation on test data' in line:
			acc_line_te = i+6
			acc_te = lines[acc_line_te].split('(')[1].split(')')[0].strip('%')
			acc_te = str(100-float(acc_te))
		if 'Rule' in line and 'lift' in line:
			j = i+1
			one_terms = []
			zero_terms = []
			while '->' not in lines[j]:
				attr, dummy, zero_one = lines[j].split()
				
				if zero_one == '0':
					one_terms.append('~' + attr)
					zero_terms.append(attr)
				if zero_one == '1':
					one_terms.append(attr)
					zero_terms.append('~' + attr)

				j += 1
			if 'class 1' in lines[j]:
				one_term_str = '*'.join(one_terms)  # SOP
				one_equation.append(one_term_str)
			if 'class 0' in lines[j]:
				zero_term_str = '+'.join(zero_terms)  # POS
				zero_equation.append(zero_term_str)

		if 'Default class' in line:
			def_class = line.strip('\n').split()[-1]

	one_equation = '+'.join(one_equation)  # SOP
	zero_equation = '*'.join(zero_equation)  # POS

	if one_equation == '':
		one_equation = '=' + def_class
	if zero_equation == '':
		zero_equation = '=' + def_class
	
	return acc_tr, acc_te, one_equation, zero_equation


output_csv = open('c50_results.csv', 'w')
print(','.join(['base_name', 'sk_acc_tree', 'sk_acc_rf', 'C50_tr_acc', 'C50_te_acc', 'eq_one']), file=output_csv)

for path in os.listdir('./'):
	if '.data' not in path:
		continue
	
	base_name = path.split('.data')[0]
	c50f_data = base_name + '.data'
	c50f_names = base_name + '.names'
	c50f_test = base_name + '.test'
	c50f_output = base_name + '.out'

	train_data = np.loadtxt(c50f_data, dtype='bool', delimiter=',')
	test_data = np.loadtxt(c50f_test, dtype='bool', delimiter=',')

	sk_acc_tree = get_test_acc_from_dtree(train_data, test_data)
	sk_acc_rf = get_train_test_acc_from_random_forest(train_data, test_data)

	try:
		tr_acc, te_acc, eq_one, eq_zero = parse_output(c50f_output)
	except:
		os.system('./C50/c5.0 -r -f %s > %s' % (base_name, c50f_output))
		C50_tr_acc, C50_te_acc, eq_one, eq_zero = parse_output(c50f_output)

	print(','.join([base_name, sk_acc_tree, sk_acc_rf, C50_tr_acc, C50_te_acc, eq_one, eq_zero]), file=output_csv)

output_csv.close()
