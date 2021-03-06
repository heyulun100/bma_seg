__author__ = 'Brian M Anderson'
# Created on 11/28/2020
from DL_Template.ReturnHparameters import return_list_of_models
from DL_Template.ReturnCosineLoss import CosineLoss
from DL_Template.ReturnGenerators import return_generators, return_paths
from Base_Deeplearning_Code.Finding_Optimization_Parameters.HyperParameters import is_df_within_another, return_hparams
from DL_Template.RunModel import run_model
import os
from DL_Template.ReturnModels import return_model
import pandas as pd
import tensorflow as tf
import types
import numpy as np


def run_2d_model(batch_size=24):
    train_generator, validation_generator = None, None
    epochs = 10001
    base_path, morfeus_drive = return_paths()

    excel_path = os.path.join(morfeus_drive, 'ModelParameters.xlsx')
    iterations = [0, 1, 2, 3]
    for cv_id in range(5):
        model_key_base = -1
        base_df = pd.read_excel(excel_path)
        base_df.set_index('Model_Index')
        potentially_not_run = base_df.loc[pd.isnull(base_df.cv_id) & ~pd.isnull(base_df.min_lr)]
        indexes_for_not_run = potentially_not_run.index.values
        np.random.shuffle(indexes_for_not_run)
        for index in indexes_for_not_run:
            run_df = base_df.loc[[index]]
            model_key = run_df.loc[index, 'Model_Type']
            run_df.at[index, 'cv_id'] = cv_id
            compare_list = ('Model_Type', 'min_lr', 'max_lr', 'step_factor', 'Iteration', 'cv_id', 'Optimizer', 'Loss')
            features_list = ('Model_Type', 'step_factor', 'Optimizer', 'min_lr', 'max_lr', 'Loss')
            if model_key == 3:
                compare_list = ('Model_Type', 'min_lr', 'max_lr', 'step_factor', 'Iteration', 'cv_id',
                                'blocks_in_dense', 'dense_conv_blocks', 'dense_layers', 'num_dense_connections',
                                'filters', 'growth_rate',
                                'Optimizer', 'Loss', 'reduction')
                features_list = ('Model_Type', 'step_factor', 'blocks_in_dense', 'dense_conv_blocks', 'dense_layers',
                                 'num_dense_connections', 'filters', 'growth_rate', 'Optimizer', 'min_lr', 'max_lr',
                                 'Loss')
            for iteration in iterations:
                run_df.at[index, 'Iteration'] = iteration
                contained = is_df_within_another(data_frame=base_df, current_run_df=run_df, features_list=compare_list)
                if contained:
                    print("Already ran this one")
                    continue
                if model_key_base != model_key or train_generator is None:
                    _, _, train_generator, validation_generator = return_generators(batch_size=batch_size,
                                                                                    cross_validation_id=cv_id,
                                                                                    cache=True, model_key=model_key)
                    model_key_base = model_key
                model_base = return_model(model_key=model_key)
                model_parameters = run_df.squeeze().to_dict()
                for key in model_parameters.keys():
                    if type(model_parameters[key]) is np.int64:
                        model_parameters[key] = int(model_parameters[key])
                    elif type(model_parameters[key]) is np.float64:
                        model_parameters[key] = float(model_parameters[key])
                opt = tf.keras.optimizers.SGD()
                loss = tf.keras.losses.CategoricalCrossentropy()
                if model_parameters['Loss'] == 'CosineLoss':
                    loss = CosineLoss()
                if model_parameters['Optimizer'] == 'SGD':
                    opt = tf.keras.optimizers.SGD()
                if isinstance(model_base, types.FunctionType):
                    model = model_base(**model_parameters)
                else:
                    model = model_base
                model_index = 0
                while model_index in base_df['Model_Index'].values:
                    model_index += 1
                run_df.at[index, 'Model_Index'] = model_index
                base_df = base_df.append(run_df)
                base_df.to_excel(excel_path, index=0)
                model_path = os.path.join(base_path, 'Models', 'Model_Index_{}'.format(model_index))
                tensorboard_path = os.path.join(morfeus_drive, 'Tensorflow', 'Model_Key_{}'.format(model_key),
                                                'Model_Index_{}'.format(model_index))
                print('Saving model to {}\ntensorboard at {}'.format(model_path, tensorboard_path))
                hparams = return_hparams(model_parameters, features_list=features_list, excluded_keys=[])
                run_model(model=model, train_generator=train_generator, validation_generator=validation_generator,
                          min_lr=model_parameters['min_lr'], max_lr=model_parameters['max_lr'], model_path=model_path,
                          tensorboard_path=tensorboard_path, trial_id=model_index, optimizer=opt, hparams=hparams,
                          step_factor=model_parameters['step_factor'], epochs=epochs, loss=loss)
                return None


if __name__ == '__main__':
    pass
