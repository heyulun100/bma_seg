__author__ = 'Brian M Anderson'
# Created on 11/24/2020
from Base_Deeplearning_Code.Finding_Optimization_Parameters.LR_Finder import make_plot, os
from DL_Template.ReturnPaths import return_paths
import pandas as pd


def plot_lrs(input_path):
    base_path, morfeus_drive = return_paths()
    excel_path = os.path.join(morfeus_drive, 'ModelParameters.xlsx')
    base_df = pd.read_excel(excel_path)
    for root, folders, files in os.walk(input_path):
        paths = [os.path.join(root, i) for i in folders if i.find('Iteration') != -1]
        if paths:
            print(root)
            desc = os.path.split(root)[-1]
            save_path = os.path.join(input_path, 'Outputs')
            try:
                out_lr_dict = make_plot(paths, metric_list=['loss'], title=desc, save_path=save_path, plot=False,
                                        auto_rates=True, beta=0.96, plot_show=False)
                if excel_path is not None:
                    model_index = int(os.path.split(paths[0])[0].split('Model_Index_')[-1])
                    index = base_df.loc[base_df.Model_Index == int(model_index)]
                    if index.shape[0] > 0:
                        index = index.index[0]
                        if pd.isnull(base_df.loc[index, 'min_lr']):
                            base_df = pd.read_excel(excel_path)
                            if pd.isnull(base_df.loc[index, 'min_lr']):
                                base_df.at[index, 'min_lr'] = out_lr_dict['loss']['min_lr']
                                base_df.at[index, 'max_lr'] = out_lr_dict['loss']['max_lr']
                                base_df.to_excel(excel_path, index=0)
            except:
                xxx = 1
    return True


if __name__ == '__main__':
    pass
