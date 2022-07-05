import os
import pprint
import numpy as np
import riskslim
import pandas as pd
import pickle
import math


def CPA_function(data_name, max_L0_value):
    # data

    data_dir = os.getcwd() + '/examples/data/'                  # directory where datasets are stored
    data_csv_file = data_dir + data_name + '_data.csv'          # csv file for the dataset
    sample_weights_csv_file = None                              # csv file of sample weights for the dataset (optional)

    # problem parameters
    max_coefficient = 5                                         # value of largest/smallest coefficient
    # max_L0_value = 12                                            # maximum model size (set as float(inf))
    max_offset = 50                                             # maximum value of offset parameter(optional)

    c0_value = 1e-6                                             # L0-penalty parameter such that c0_value > 0; larger values -> sparser models; we set to a small value (1e-6) so that we get a model with max_L0_value terms


    # load data from disk
    data = riskslim.load_data_from_csv(dataset_csv_file = data_csv_file, sample_weights_csv_file = sample_weights_csv_file)

    df = pd.read_csv(data_csv_file)
    # print('SHAPE is',df.shape)

    # create coefficient set and set the value of the offset parameter
    coef_set = riskslim.CoefficientSet(variable_names = data['variable_names'], lb = -max_coefficient, ub = max_coefficient, sign = 0)
    coef_set.update_intercept_bounds(X = data['X'], y = data['Y'], max_offset = max_offset)

    constraints = {
        'L0_min': 0,
        'L0_max': max_L0_value,
        'coef_set':coef_set,
    }

    # major settings (see riskslim_ex_02_complete for full set of options)
    settings = {
        # Problem Parameters
        'c0_value': c0_value,
        #
        # LCPA Settings
        'max_runtime': 30.0,                               # max runtime for LCPA
        'max_tolerance': np.finfo('float').eps,             # tolerance to stop LCPA (set to 0 to return provably optimal solution)
        'display_cplex_progress': True,                     # print CPLEX progress on screen
        'loss_computation': 'fast',                         # how to compute the loss function ('normal','fast','lookup')
        #
        # LCPA Improvements
        'round_flag': True,                                # round continuous solutions with SeqRd
        'polish_flag': True,                               # polish integer feasible solutions with DCD
        'chained_updates_flag': True,                      # use chained updates
        'add_cuts_at_heuristic_solutions': True,            # add cuts at integer feasible solutions found using polishing/rounding
        #
        # Initialization
        'initialization_flag': True,                       # use initialization procedure
        'init_max_runtime': 120.0,                         # max time to run CPA in initialization procedure
        'init_max_coefficient_gap': 0.49,
        #
        # CPLEX Solver Parameters
        'cplex_randomseed': 0,                              # random seed
        'cplex_mipemphasis': 0,                             # cplex MIP strategy
    }

    # train model using lattice_cpa
    model_info, mip_info, lcpa_info = riskslim.run_lattice_cpa(data, constraints, settings)

    #print model contains model
    riskslim.print_model(model_info['solution'], data)

    #model info contains key results
    pprint.pprint(model_info)
    
    v = np.dot(data['X'], model_info['solution'])
    v = v.astype(np.float32)
    
    # get pred vals and pred prob
    prob = np.exp(v)/(1.0 + np.exp(v))

    pred_vals = np.zeros(shape=np.shape(prob))
    
    for i in range(len(prob)):
        if prob[i] >= 0.5:
            pred_vals[i] = 1.0
        else:
            pred_vals[i] = 0.0
            
    return model_info, prob, pred_vals

# Write to file
# model_result = pd.DataFrame(list(df.columns)).copy()
# model_result.insert(len(model_result.columns),"Coefs",model_info['solution'])
# model_result.rename(columns = {0:'Features'}, inplace = True)
# model_result.to_csv('/Users/zhaotongtong/Desktop/Risk_Model_Research/risk-slim/examples/results/cpa_breastcancer.csv')
# filter_model_result = model_result[(model_result['Coefs'] != 0.0) & (model_result['Coefs'] !=-0.0) ]
# filter_model_result.to_csv('/Users/zhaotongtong/Desktop/Risk_Model_Research/risk-slim/examples/results/filter_cpa_breastcancer.csv')
# with pd.ExcelWriter('/Users/zhaotongtong/Desktop/Risk_Model_Research/risk-slim/examples/results/result_compare.xlsx',
#                     mode='a') as writer:  
#     filter_model_result.to_excel(writer, sheet_name='filter_cpa_breastcancer') 


#-------sample CPA-----------

model_info, prob_tb, pred_vals_tb = CPA_function('tbrisk_cpa', 12)


print(pred_vals_tb)
print('-------')
print(model_info['solution'])
print('-------')
print(prob_tb)

cm = fp, fn, tp, tn

confusion_matrix(data['Y'], pred_vals_)