all: c5.0

c5.0: attwinnow.o c50.o classify.o confmat.o construct.o contin.o discr.o formrules.o formtree.o getdata.o getnames.o global.o implicitatt.o info.o mcost.o modelfiles.o p-thresh.o prune.o report.o rules.o ruletree.o siftrules.o sort.o subset.o trees.o update.o utility.o xval.o
	g++ -g3 attwinnow.o c50.o classify.o confmat.o construct.o contin.o discr.o formrules.o formtree.o getdata.o getnames.o global.o implicitatt.o info.o mcost.o modelfiles.o p-thresh.o prune.o report.o rules.o ruletree.o siftrules.o sort.o subset.o trees.o update.o utility.o xval.o -o c5.0 -fopenmp

attwinnow.o: attwinnow.c
	g++ -g3 -c attwinnow.c

c50.o: c50.c
	g++ -g3 -c c50.c

classify.o: classify.c
	g++ -g3 -c classify.c

confmat.o: confmat.c
	g++ -g3 -c confmat.c

construct.o: construct.c
	g++ -g3 -c construct.c

contin.o: contin.c
	g++ -g3 -c contin.c

discr.o: discr.c
	g++ -g3 -c discr.c

formrules.o: formrules.c
	g++ -g3 -c formrules.c

formtree.o: formtree.c
	g++ -g3 -c formtree.c

getdata.o: getdata.c
	g++ -g3 -c getdata.c

getnames.o: getnames.c
	g++ -g3 -c getnames.c

global.o: global.c
	g++ -g3 -c global.c

implicitatt.o: implicitatt.c
	g++ -g3 -c implicitatt.c

info.o: info.c
	g++ -g3 -c info.c

mcost.o: mcost.c
	g++ -g3 -c mcost.c

modelfiles.o: modelfiles.c
	g++ -g3 -c modelfiles.c

p-tresh.o: p-thresh.c
	g++ -g3 -c p-thresh.c

prune.o: prune.c
	g++ -g3 -c prune.c

report.o: report.c
	g++ -g3 -c report.c

rules.o: rules.c
	g++ -g3 -c rules.c

ruletree.o: ruletree.c
	g++ -g3 -c ruletree.c

siftrules.o: siftrules.c
	g++ -g3 -c siftrules.c

sort.o: sort.c
	g++ -g3 -c sort.c

subset.o: subset.c
	g++ -g3 -c subset.c

trees.o: trees.c
	g++ -g3 -c trees.c

update.o: update.c
	g++ -g3 -c update.c

utility.o: utility.c
	g++ -g3 -c utility.c

xval.o: xval.c
	g++ -g3 -c xval.c

clean:
	rm *.o
