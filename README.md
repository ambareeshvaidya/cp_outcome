# To Cut Or Not To Cut, That Is The Question

Cutting planes, or cuts, are a relaxation-tightening technique employed by mixed-integer programming solvers, due to cuts’ beneficial effect on average across diverse instances. However, cuts do not always help. We study the effect of the cuts parameter in SCIP, an open-source optimization solver, using instances from the 2017 Mixed Integer Programming Library. Our results verify that, although the default setting of cuts-on does provide on average a faster solving time than cuts-off, a significant number of instances are actually solved faster by disabling cuts. Further, we train a classifier to approximate the virtual best solver for whether to set the parameter cuts-on or cuts-off for each instance. We achieve this by collecting early indicators at three points in the solver to make a binary decision (cuts-on/cuts-off).

# Notes
We use Python 3.8 and SCIP 8.0 with its python API PySCIPOpt 4.2.0. The numpy and pandas libraries are employed for data manipulation, all plotting is done with matplotlib and seaborn and we employ scikit-learn for the machine learning experiments.
