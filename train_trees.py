from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import _tree
import numpy as np
from math import sqrt, ceil
from itertools import combinations
from sklearn.model_selection import train_test_split

from sklearn.feature_selection import SelectKBest, SelectPercentile
from sklearn.feature_selection import chi2, f_classif, mutual_info_classif
from copy import deepcopy
from sklearn.tree import *

function_mappings = {
	'chi2': chi2,
	'f_classif': f_classif,
	'mutual_info_classif': mutual_info_classif,
}


def fillWithZeroes(X, X_new):
	X_new2 = deepcopy(X)
	i = 0
	for column in X.T:
		found = 0
		for compColumn in X_new.T:
			if np.array_equal(column, compColumn):
				found = 1
				break
		if found == 0:
			X_new2[:i] = 0
		i += 1

	return X_new2


def pythonizeSOP(sop):
	or_list = []

	if not sop:
		expr = '((x0) * !(x0))'
		return expr

	for ands in sop:
		and_list = []
		and_expr = '('
		for attr, negated in ands:
			if negated == 'true':
				and_list.append(f'!(x{int(attr):02d})')
			else:
				and_list.append(f'(x{int(attr):02d})')
		and_expr += ' * '.join(and_list)
		and_expr += ')'
		or_list.append(and_expr)
	expr = f'({" + ".join(or_list)})'
	return expr


def pythonizeRF(sopRF):
	exprs = []
	for sopDT in sopRF:
		exprs.append(pythonizeSOP(sopDT))

	print(exprs)
	if exprs == []:
		finalExpr = '((x0) * !(x0))'
		return finalExpr

	nrInputsMaj = len(exprs)
	sizeTermMaj = int(ceil(nrInputsMaj/2.0))
	ands = []

	for comb in combinations(exprs, sizeTermMaj):
		ands.append(" and ".join(comb))

	finalExpr = '(%s)' % (") or (".join(ands))

	return finalExpr


def trainMajorityRF(train_data, test_data, test2_data, num_trees = 100, apply_SKB = 0, apply_SP = 0, score_f = "chi2", thr = 0.8, k = 10, percent = 50, depth = 10, useDefaultDepth= 1):
	Xtr, ytr = train_data[:,:-1], train_data[:,-1]
	Xte, yte = test_data[:,:-1], test_data[:,-1]
	Xte2, yte2 = test2_data[:,:-1], test2_data[:,-1]
	Xtr_new = deepcopy(Xtr)

	if apply_SKB == 1:
		selector = SelectKBest(function_mappings[score_f], k = k)
		selector.fit(Xtr, ytr)
		Xtr_new = selector.transform(Xtr)
		Xtr_new = fillWithZeroes(Xtr, Xtr_new)

	if apply_SP == 1:
		selector = SelectPercentile(function_mappings[score_f], percentile=percent)
		selector.fit(Xtr, ytr)
		Xtr_new = selector.transform(Xtr)
		Xtr_new = fillWithZeroes(Xtr, Xtr_new)

	num_feats_sub = int(sqrt(Xtr_new.shape[1]))
	num_feats = Xtr_new.shape[1]
	trees = []
	votes = []
	votes2 = []
	for i in range(num_trees):
		cols_idx = np.random.choice(range(num_feats), num_feats - num_feats_sub)

		Xtr_sub = np.array(Xtr_new)
		Xtr_sub[:,cols_idx] = 1
		tree = None
		if useDefaultDepth == 1:
			tree = DecisionTreeClassifier().fit(Xtr_sub, ytr)
		else:
			tree = DecisionTreeClassifier(max_depth=depth).fit(Xtr_sub, ytr)
		trees.append(tree)
		votes.append(tree.predict(Xte))
		votes2.append(tree.predict(Xte2))
	votes = np.array(votes).T
	votes2 = np.array(votes2).T
	final_vote = np.round(votes.sum(axis=1)/float(num_trees)).astype('int')
	final_vote2 = np.round(votes2.sum(axis=1)/float(num_trees)).astype('int')
	acc = (final_vote == yte).mean()
	acc2 = (final_vote2 == yte2).mean()
	#print(acc)

	return trees, acc, acc2


def eval_single(d, eqn_str):
	eqn_str_orig = eqn_str

	for i, d_ in enumerate(d):
		eqn_str = eqn_str.replace('x%d)' % i, (str(d_)+')'))

	return int(eval(eqn_str))


def eval_equation(eqn_str, data):
	X, y = data[:, :-1], data[:, -1]
	ypred = np.apply_along_axis(eval_single, 1,  X, eqn_str)
	return str((np.equal(ypred, y, dtype=int)).mean())


def treeToSOP(tree, featureNames):
	tree_ = tree.tree_
	featureName = [featureNames[i] if i != _tree.TREE_UNDEFINED else "undefined!" for i in tree_.feature]

	ors = []

	if tree_.feature[0] == _tree.TREE_UNDEFINED:
		if np.argmax(tree_.value[0]) == 1:
			ors.append([['1', 'true']])
			ors.append([['1', 'false']])
		return ors

	def recurse(node, depth, expression):
		if tree_.feature[node] != _tree.TREE_UNDEFINED:
			name = featureName[node]

			recurse(tree_.children_left[node], depth + 1, deepcopy(expression + [[name, 'true']]))

			recurse(tree_.children_right[node], depth + 1, deepcopy(expression + [[name, 'false']]))
		else:
			if np.argmax(tree_.value[node]) == 1:
				ors.append(deepcopy(expression))

	recurse(0, 1, [])

	return ors


def forestToSOP(forest, featureNames):
	sops = []
	for tree in forest:
		sop = treeToSOP(tree, featureNames)
		sops.append(sop)
	return sops


def trainTree(Xtr, ytr, max_depth=0):
	if max_depth == 0:
		tree = DecisionTreeClassifier().fit(Xtr, ytr)
	else:
		tree = DecisionTreeClassifier(max_depth=max_depth).fit(Xtr, ytr)

	ypred_tree = tree.predict(Xtr)
	acc_tree = (ypred_tree == ytr).mean()

	print(f'accuracy = {acc_tree}')

	return tree, acc_tree


def trainRandomForest(train_data, test_data):
	Xtr, ytr = train_data[:, :-1], train_data[:, -1]
	Xte, yte = test_data[:, :-1], test_data[:, -1]

	rf = RandomForestClassifier().fit(Xtr, ytr)

	ypred_rf = rf.predict(Xte)

	acc_rf = (ypred_rf == yte).mean()

	return rf, acc_rf


def mixTrainTest(train_data, test_data, splitRatio=0.25):
	full_data = np.concatenate((train_data, test_data))
	Xfull, yfull = full_data[:, :-1], full_data[:, -1]
	Xtr, Xte, ytr, yte = train_test_split(Xfull, yfull, test_size=splitRatio, random_state=0)
	train_data_mix = np.concatenate((Xtr, ytr.reshape(int(12800*(1-splitRatio)), 1)), axis=1)
	test_data_mix = np.concatenate((Xte, yte.reshape(int(12800*splitRatio), 1)), axis=1)
	return train_data_mix, test_data_mix


