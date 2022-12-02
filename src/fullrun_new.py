from pyscipopt import Model, SCIP_PARAMSETTING, Eventhdlr, SCIP_EVENTTYPE 
import argparse    
import os
import csv
import os.path
import traceback

parser = argparse.ArgumentParser(description = 'Parser for data_extract script')
parser.add_argument('--instance', type = str, required =True, help = 'Name of the MIP instance')
parser.add_argument('--cuts', type = float, required =True, help = 'Cuts off: 0, Default cuts: 1' )
parser.add_argument('--seed', type = float, required =True, help = 'Set random seed' )
parser.add_argument('--result_path', type = str, required = True, help = 'Absolute path to results')
parser.add_argument('--threads', type = float, default = 8, help = 'Set number of threads' )

ARGS = parser.parse_args()

# Set parameters for instance
def set_parameters(model, ARGS):
    
    model.setIntParam("branching/random/seed", ARGS.seed)
    model.setIntParam("parallel/maxnthreads", ARGS.threads)
    model.setRealParam("limits/time", 18000)
    
    if ARGS.cuts == 0:
        model.setSeparating(SCIP_PARAMSETTING.OFF)
    elif ARGS.cuts == 1:
        model.setSeparating(SCIP_PARAMSETTING.DEFAULT)

# Set parameters for LP of instance  
def set_lp_relax_parameters(model, ARGS):
    
    model.setIntParam("branching/random/seed", ARGS.seed)
    model.setIntParam("parallel/maxnthreads", ARGS.threads)
    model.setRealParam("limits/time", 18000)
    
    if ARGS.cuts == 0:
        model.setSeparating(SCIP_PARAMSETTING.OFF)
    elif ARGS.cuts == 1:
        model.setSeparating(SCIP_PARAMSETTING.DEFAULT)
        
    model.setPresolve(SCIP_PARAMSETTING.OFF)
    
    for v in model.getVars():
        model.chgVarType(v, 'CONTINUOUS')
        
class MyEvent(Eventhdlr):
    
    def __init__(self, init_lp, init_time, lp_first_round, lp_root_end, time_cut_rounds, cut_rounds_root, cut_gen):
        self.init_lp = init_lp
        self.init_time = init_time
        self.lp_first_round = lp_first_round
        self.lp_root_end = lp_root_end
        self.time_cut_rounds = time_cut_rounds
        self.cut_rounds_root = cut_rounds_root
        self.cut_gen = cut_gen
        
    def eventinit(self):
        self.model.catchEvent(SCIP_EVENTTYPE.FIRSTLPSOLVED | SCIP_EVENTTYPE.ROWADDEDSEPA | SCIP_EVENTTYPE.LPSOLVED | SCIP_EVENTTYPE.NODEFOCUSED | 
                             SCIP_EVENTTYPE.NODESOLVED, self)

    def eventexit(self):
        self.model.dropEvent(SCIP_EVENTTYPE.FIRSTLPSOLVED | SCIP_EVENTTYPE.ROWADDEDSEPA | SCIP_EVENTTYPE.LPSOLVED | SCIP_EVENTTYPE.NODEFOCUSED | 
                             SCIP_EVENTTYPE.NODESOLVED, self)

    def eventexec(self, event):
        node_count = self.model.getNNodes()
        cut_applied = self.model.getNCutsApplied()
        
# (i) the initial LP value before the root node starts processing
        if node_count == 1 and cut_applied == 0:
            best_bnd = self.model.getObjVal()
            self.init_time.append(self.model.getSolvingTime())
            if best_bnd != +1e+20 and best_bnd != -1e+20 and best_bnd != 0:
                self.init_lp.append(best_bnd)
                
# (ii) the LP value after the first round of cuts
        if cut_applied != 0 and node_count == 1:
            self.lp_first_round.append(self.model.getObjVal())
            self.time_cut_rounds.append(self.model.getSolvingTime())

# (iii) the number of rounds of cuts at the root node
        if node_count == 1:
            self.cut_rounds_root.append(cut_applied)
                      
# (iv)  the LP value at the end of the processing of the root node (right before branching starts)
        if node_count == 1:
            root_end = self.model.getObjVal()
            if root_end != +1e+20 and root_end != -1e+20 and root_end != 0:
                self.lp_root_end.append(root_end)
        
# (v)  cuts generated during solve
        self.cut_gen.append(self.model.getNCuts())

# Append data to csv
def tocsv(name, init_lp_value, lp_first_round_cuts, total_cut_rounds, lp_root_end_value, obj_val, sol_time, presol_time, primal_bd, gp, total_cut_gen, cut_applied, n_cuts, node_count, init_lp_time, time_first_round, time_root_end, seed, cut_set, status, remark):
   
    data = [name, init_lp_value, lp_first_round_cuts, total_cut_rounds, lp_root_end_value, obj_val, sol_time, presol_time, primal_bd, gp, total_cut_gen, cut_applied, n_cuts, node_count, init_lp_time, time_first_round, time_root_end, seed, cut_set, status, remark]
    header = ["NAME", "INITIAL LP", "FIRST ROUND CUT", "ROUND OF CUTS", "OBJECTIVE VALUE ROOT NODE", "BEST SOLUTION", "SOLUTION TIME", "PRESOLVING TIME", "BEST PRIMAL BOUND", "GAP", "No. OF CUTS GENERATED",
              "No. OF CUTS APPLIED", "No. OF CUTS PRESENT IN LP AT THE END", "No. OF NODES", "INITIAL LP TIME", "TIME FIRST ROUND", "TIME ROOT END", "RANDOM SEED", "CUT SETTING", "STATUS", "END"]
        
    with open(ARGS.result_path + '/result.csv', 'a') as f:
        file_is_empty = os.stat(ARGS.result_path + '/result.csv').st_size==0
        writer = csv.writer(f, lineterminator='\n')
        if file_is_empty:
            writer.writerow(header)
        writer.writerow(data)        

# Data Collect
def data_collect():   
    model = Model()
    model.readProblem(ARGS.instance)
    set_parameters(model, ARGS)

        
    # Variables
    init_lp = []
    init_time = []
    lp_first_round = []
    lp_root_end = [] 
    time_cut_rounds = []
    cut_rounds_root = []
    cut_gen = []
    
    # Event Handler Call
    eventhdlr = MyEvent(init_lp, init_time, lp_first_round, lp_root_end, time_cut_rounds, cut_rounds_root, cut_gen)
    model.includeEventhdlr(eventhdlr, "Node Event", "python event handler to catch NODE EVENT")
    
    # Optimize model
    model.optimize()
    
    # This loop is to find the number of rounds of cuts 
    total_cut_rounds = 0
    for i in range(len(cut_rounds_root)):
        if cut_rounds_root[i] > cut_rounds_root[i-1]:
            total_cut_rounds += 1
    
    # This loop is to find the number of cuts generated
    total_cut_gen = 0
    for i in range(len(cut_gen)):
        if cut_gen[i] > cut_gen[i-1]:
            total_cut_gen += 1
    
    # Initial LP before root node starts processing
    init_lp_value = init_lp[0] if init_lp else 0
    
    # LP value after first round of cuts
    lp_first_round_cuts = lp_first_round[0] if lp_first_round else 0
    
    # LP at the end of root node 
    lp_root_end_value = lp_root_end[-1] if lp_root_end else 0
    
    # time
    init_lp_time = init_time[0] if init_time else 0
    time_first_round = time_cut_rounds[0] if time_cut_rounds else 0
    time_root_end = time_cut_rounds[-1] if time_cut_rounds else 0
    
    obj_val = model.getObjVal()
    sol_time = model.getSolvingTime()
    presol_time = model.getPresolvingTime()
    primal_bd = model.getPrimalbound()
    gp = model.getGap()
    node_count = model.getNNodes()
    cut_applied = model.getNCutsApplied()
    n_cuts = model.getNCuts()
    status = model.getStatus()
    remark = 'DONE'
    
    # Solve LP relaxation
    def lp_relax():
        lp = Model()
        lp.readProblem(ARGS.instance)
        set_lp_relax_parameters(lp, ARGS)
        
        print('SOLVING LP RELAXATION')
        # Optimize model
        lp.optimize()
        
        obj_val = lp.getObjVal()
        sol_time = lp.getSolvingTime()
        presol_time = model.getPresolvingTime() + lp.getPresolvingTime()
        primal_bd = lp.getPrimalbound()
        gp = lp.getGap()
        node_count = lp.getNNodes()
        cut_applied = lp.getNCutsApplied()
        n_cuts = lp.getNCuts()
        status = lp.getStatus()
        
        # Initialize LP value
        node_count = lp.getNNodes()
        if node_count == 1:
            best_bnd = lp.getObjVal()
            if best_bnd != +1e+20 and best_bnd != -1e+20 and best_bnd != 0:
                init_lp.append(best_bnd)
            
            # LP value at the end of root node
        if node_count == 1:
            lp_root_end.append(lp.getObjVal())
                
                
        init_lp_value = init_lp[0] if init_lp else 0
        lp_root_end_value = lp_root_end[-1] if lp_root_end else 0
        # time
        init_lp_time = init_time[0] if init_time else 0
        time_first_round = time_cut_rounds[0] if time_cut_rounds else 0
        time_root_end = time_cut_rounds[-1] if time_cut_rounds else 0
    
        remark = "DONE SOLVED THROUGH LP RELAXATION"
        tocsv(name, init_lp_value, lp_first_round_cuts, total_cut_rounds, lp_root_end_value, obj_val, sol_time, presol_time, primal_bd, gp, total_cut_gen, cut_applied, n_cuts, node_count, init_lp_time, time_first_round, time_root_end, seed, cut_set, status, remark)
    
    # Check if instance is solved at presolve or print to csv   
    if (model.getNNodes() < 1):
        lp_relax()
    else:
        tocsv(name, init_lp_value, lp_first_round_cuts, total_cut_rounds, lp_root_end_value, obj_val, sol_time, presol_time, primal_bd, gp, total_cut_gen, cut_applied, n_cuts, node_count, init_lp_time, time_first_round, time_root_end, seed, cut_set, status, remark)
   
# main
if __name__ == "__main__":
   
    name = ARGS.instance.split('/')[4]
    seed = int(ARGS.seed)
    cut_set = int(ARGS.cuts)
    # error handling
    try:
        data_collect()
    except Exception as error:
        traceback.print_exc()
        data = [name,'','','','','','','','','','','','','', seed, cut_set, repr(error), "ERROR"]
        header = ["NAME", "INITIAL LP", "FIRST ROUND CUT", "ROUND OF CUTS", "OBJECTIVE VALUE ROOT NODE", "BEST SOLUTION", "SOLUTION TIME", "PRESOLVING TIME", "BEST PRIMAL BOUND", "GAP", "No. OF CUTS GENERATED",
              "No. OF CUTS APPLIED", "No. OF CUTS PRESENT IN LP AT THE END", "No. OF NODES", "RANDOM SEED", "CUT SETTING", "STATUS", "END"]
        
        
        with open(ARGS.result_path + '/result.csv', 'a') as f:
            file_is_empty = os.stat(ARGS.result_path + '/result.csv').st_size==0
            writer = csv.writer(f, lineterminator='\n')
            if file_is_empty:
                writer.writerow(header)
            writer.writerow(data)
        
