# To Cut Or Not To Cut, That Is The Question

Cutting planes, or cuts, are a relaxation-tightening technique employed by mixed-integer programming solvers, due to cuts’ beneficial effect on average across diverse instances. However, cuts do not always help. We study the effect of the cuts parameter in SCIP, an open-source optimization solver, using instances from the 2017 Mixed Integer Programming Library. Our results verify that, although the default setting of cuts-on does provide on average a faster solving time than cuts-off, a significant number of instances are actually solved faster by disabling cuts. Further, we train a classifier to approximate the virtual best solver for whether to set the parameter cuts-on or cuts-off for each instance. We achieve this by collecting early indicators at three points in the solver to make a binary decision (cuts-on/cuts-off).

**Notes**  
We use Python 3.8 and SCIP 8.0 with its python API PySCIPOpt 4.2.0. The `numpy` and `pandas` libraries are employed for data manipulation, all plotting is done with `matplotlib` and `seaborn` and we employ `scikit-learn` for the machine learning experiments.

We divide the implementation into three main steps:
* Data Collection: each instance is run with five different (consistent) random seeds once each by setting the cuts parameter to on/off. We extract vital information during the solving process using `callbacks` that have already been implemented in PySCIPOpt. This data as well as data available directly from the MIPLIB website is used to make the final features for each instance.
* Ablation Study: once the data is compiled and cleaned for any irregularities we conduct the ablation study to determine the efficacy of the `cuts-on` setting.
* Machine Learning Experiments: we prepare the data to conduct three separate machine learning experiments

**General Pipeline**  
For the data collection step we use the cluster present at the University of Florida. To submit and schedule jobs on the alloted cores run the bash scripts in the following sequence:

`prepare_job_list.sh`: creates a `job_list.txt` file. Each line of this file contains the commands that we use to provide an input to the solver and path to store the output after the job completion.  
`run_job_list.sh`: actually runs each line of the `job_list.txt`. Note: configure the SBATCH commands according to your application.  
`merge.sh`: compile all result/error csv files into one master results/error csv file.

`fullrun_new.py`: runs an instance, seed and cuts parameter combination to extract information at predefined points during the resolution of the instance. Note: this code does not need to be run exclusively, it is executed when the `run_job_list.sh` script is run.

`Sets and ablation study.ipynb`: code and result for ablation study and creation of four data sets: `Set 1`, `Set 2`, `Set 1,2` and `Set 4` 

`Experiment 1.ipynb`: machine learning experiment and results for `Set_1,2` using data extracted until before the root node starts processing. 
`Experiment 2.ipynb`: machine learning experiment and results for `Set_1,2` using data extracted until after one round of cuts is generated and applied at the root node.  
`Experiment 3.ipynb`: machine learning experiment and results for `Set_1,2` using features extracted until the end of the root node is reached.

`Affected Instances Experiment 2.ipynb`: contains the code for further analysis of the result of experiment 2 and effects of weights on affected instances.
`Miclassified visualization.ipynb`: a visualization code of the performance of the three ML experiments.


