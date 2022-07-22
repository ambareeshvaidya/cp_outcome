from pyscipopt import Model, SCIP_PARAMSETTING, Eventhdlr, SCIP_EVENTTYPE 
import argparse    
import os
import csv
import sys
import os.path

parser = argparse.ArgumentParser(description = 'Parser for data_extract script')

parser.add_argument('--instance', type = str, required =True, help = 'Name of the MIP instance')

parser.add_argument('--cuts', type = float, required =True, help = 'Cuts off: 0, Default cuts: 1' )

parser.add_argument('--seed', type = float, required =True, help = 'Set random seed' )

parser.add_argument('--threads', type = float, default = 8, help = 'Set number of threads' )

parser.add_argument('--result_path', type = str, required = True, help = 'Absolute path to results')

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
    
    def __init__(self, init_lp, lp_first_round, lp_root_end, cut_rounds_root, cut_gen):
        self.init_lp = init_lp
        self.lp_first_round = lp_first_round
        self.lp_root_end = lp_root_end
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
            if best_bnd != +1e+20 and best_bnd != -1e+20 and best_bnd != 0:
                self.init_lp.append(best_bnd)
                
# (ii) the LP value after the first round of cuts
        if cut_applied != 0 and node_count == 1:
            self.lp_first_round.append(self.model.getObjVal())

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
        
def test_event():   
    model = Model()
    model.readProblem(ARGS.instance)
    set_parameters(model, ARGS)

        
    # Variables:
    name = ARGS.instance.split('/')[4]
    init_lp = []
    lp_first_round = []
    lp_root_end = [] 
    cut_rounds_root = []
    cut_gen = []
    remark = 'DONE'
    
    # Event Handler Call
    eventhdlr = MyEvent(init_lp, lp_first_round, lp_root_end, cut_rounds_root, cut_gen)
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
    
    # Function for solving relaxation of problem
    def lp_relax():
        os.chdir(ARGS.inst_path)
        lp = Model()
        lp.readProblem(ARGS.instance)
        set_lp_relax_parameters(lp, ARGS)
        
        # Optimize model
        lp.optimize()
        
        # Initialize LP value
        node_count = lp.getNNodes()
        if node_count == 1:
            best_bnd = lp.getObjVal()
            if best_bnd != +1e+20 and best_bnd != -1e+20 and best_bnd != 0:
                init_lp.append(best_bnd)
        
        # LP value at the end of root node
        if node_count == 1:
            lp_root_end.append(lp.getObjVal())
    
    # Check if instance is solved at presolve    
    if (model.getNNodes() < 1):
        lp_relax()
        init_lp_value = init_lp[0] if init_lp else 0
        lp_root_end_value = lp_root_end[-1] if lp_root_end else 0
        # presolve_time = lp.PresolvingTime()
        remark = "DONE SOLVED THROUGH LP RELAXATION"
    
    # Append data to csv
    data = [name, init_lp_value, lp_first_round_cuts, total_cut_rounds, lp_root_end_value, model.getObjVal(), model.getSolvingTime(), model.getPresolvingTime(), model.getPrimalbound(), model.getGap(), total_cut_gen, model.getNCutsApplied(), model.getNCuts(), model.getNNodes(), model.getStatus(), remark]
    header = ["NAME", "INITIAL LP", "FIRST ROUND CUT", "ROUND OF CUTS", "OBJECTIVE VALUE ROOT NODE", "BEST SOLUTION", "SOLUTION TIME", "PRESOLVING TIME", "BEST PRIMAL BOUND", "GAP", "No. OF CUTS GENERATED",
              "No. OF CUTS APPLIED", "No. OF CUTS PRESENT IN LP AT THE END", "No. OF NODES", "STATUS", "END"
              ]
        
    with open(ARGS.result_path + '/result.csv', 'a') as f:
        file_is_empty = os.stat(ARGS.result_path + '/result.csv').st_size==0
        writer = csv.writer(f, lineterminator='\n')
        if file_is_empty:
            writer.writerow(header)
        writer.writerow(data)

# main
if __name__ == "__main__":
    test_event()
