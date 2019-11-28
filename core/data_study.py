import os
import sys
current_path=os.path.dirname(__file__)
parentdir = os.path.dirname(current_path)

#Adding Path to various Modules
sys.path.append("../core")
sys.path.append("../visualization")
sys.path.append("../utilities")
sys.path.append("../datasets")
sys.path.append("../trained_models")
sys.path.append("../config")
#path_var=os.path.join(os.path.dirname(__file__),"../utilities")
#sys.path.append(path_var)
#sys.path.insert(0,parentdir) 

#Importing Required Modules
import pathlib
import numpy as np
import pandas as pd
import tensorflow as tf
from keras import backend as K
from tqdm import tqdm
import plotly as py
import plotly.graph_objects as go
import cufflinks as cf
K.clear_session()

#Importing Config files
import assemblyconfig_halostamping as config
import modelconfig_train as cftrain

#Importing required modules from the package
from measurement_system import HexagonWlsScanner
from assembly_system import VRMSimulationModel
from wls400a_system import GetInferenceData
from data_import import GetTrainData
from core_model import DLModel
from training_viz import TrainViz
from metrics_eval import MetricsEval
from model_train import TrainModel

	
if __name__ == '__main__':

	print('Parsing from Assembly Config File....')

	data_type=config.assembly_system['data_type']
	application=config.assembly_system['application']
	part_type=config.assembly_system['part_type']
	part_name=config.assembly_system['part_name']
	data_format=config.assembly_system['data_format']
	assembly_type=config.assembly_system['assembly_type']
	assembly_kccs=config.assembly_system['assembly_kccs']	
	assembly_kpis=config.assembly_system['assembly_kpis']
	voxel_dim=config.assembly_system['voxel_dim']
	point_dim=config.assembly_system['point_dim']
	voxel_channels=config.assembly_system['voxel_channels']
	noise_type=config.assembly_system['noise_type']
	mapping_index=config.assembly_system['mapping_index']
	file_names_x=config.assembly_system['data_files_x']
	file_names_y=config.assembly_system['data_files_y']
	file_names_z=config.assembly_system['data_files_z']
	system_noise=config.assembly_system['system_noise']
	aritifical_noise=config.assembly_system['aritifical_noise']
	data_folder=config.assembly_system['data_folder']
	kcc_folder=config.assembly_system['kcc_folder']
	kcc_files=config.assembly_system['kcc_files']


	print('Parsing from Training Config File')

	batch_size=cftrain.data_study_params['batch_size']
	epocs=cftrain.data_study_params['epocs']
	no_of_splits=cftrain.data_study_params['no_of_splits']
	min_train_samples=cftrain.data_study_params['min_train_samples']
	split_ratio=cftrain.data_study_params['split_ratio']


	print('Creating file Structure....')
	folder_name=part_type
	train_path='../trained_models/'+part_type
	pathlib.Path(train_path).mkdir(parents=True, exist_ok=True) 

	model_path=train_path+'/model'
	pathlib.Path(model_path).mkdir(parents=True, exist_ok=True)
	
	logs_path=train_path+'/logs'
	pathlib.Path(logs_path).mkdir(parents=True, exist_ok=True)

	plots_path=train_path+'/plots'
	pathlib.Path(plots_path).mkdir(parents=True, exist_ok=True)

	deployment_path=train_path+'/deploy'
	pathlib.Path(deployment_path).mkdir(parents=True, exist_ok=True)

	#Objects of Measurement System, Assembly System, Get Infrence Data
	print('Intilizing the Assembly System and Measurement System....')
	measurement_system=HexagonWlsScanner(data_type,application,system_noise,part_type,data_format)
	vrm_system=VRMSimulationModel(assembly_type,assembly_kccs,assembly_kpis,part_name,part_type,voxel_dim,voxel_channels,point_dim,aritifical_noise)
	get_data=GetTrainData();

	print('Importing and Preprocessing Cloud-of-Point Data')
	dataset=[]
	dataset.append(get_data.data_import(file_names_x,data_folder))
	dataset.append(get_data.data_import(file_names_y,data_folder))
	dataset.append(get_data.data_import(file_names_z,data_folder))
	point_index=get_data.load_mapping_index(mapping_index)

	kcc_dataset=get_data.data_import(kcc_files,kcc_folder)
	
	input_conv_data, kcc_subset_dump,kpi_subset_dump=get_data.data_convert_voxel_mc(vrm_system,dataset,point_index,kcc_dataset)
	#print(input_conv_data.shape,kcc_subset_dump.shape)

	print('Training 3D CNN model')
	tensorboard_str='tensorboard' + '--logdir '+logs_path
	print('Vizavlize at Tensorboard using ', tensorboard_str)
	
	output_dimension=assembly_kccs
	max_dim=len(input_conv_data)
	div_dim=int((len(input_conv_data)-min_train_samples)/no_of_splits)

	eval_metrics_type= ["Mean Absolute Error","Mean Squared Error","Root Mean Squared Error","R Squared"]

	kcc_id=[]

	for i in range(assembly_kccs):  
		kcc_name="KCC_"+str(i+1)
		kcc_id.append(kcc_name)

	datastudy_output=np.zeros((no_of_splits+1,(assembly_kccs+1)*len(eval_metrics_type)+1))
	
	for i in tqdm(range(no_of_splits+1)):
		
		run_id=i
		train_dim=min_train_samples+(i*div_dim)
		if(train_dim>max_dim):
			train_dim=max_dim
		
		print("  Conducting datastudy study on :",train_dim, " samples")
		train_model=TrainModel(batch_size,epocs)
		input_conv_subset=input_conv_data[0:train_dim,:,:,:,:]
		kcc_subset=kcc_subset_dump[0:train_dim,:]

		print('Building 3D CNN model')

	
		dl_model=DLModel(output_dimension)
		model=dl_model.cnn_model_3d(voxel_dim,voxel_channels)
		
		trained_model,eval_metrics,accuracy_metrics_df=train_model.run_train_model(model,input_conv_subset,kcc_subset,model_path,logs_path,plots_path,split_ratio,run_id)


		datastudy_output[i,0]=train_dim
		datastudy_output[i,1:assembly_kccs+1]=eval_metrics["Mean Absolute Error"]
		datastudy_output[i,assembly_kccs+1:(2*assembly_kccs)+1]=eval_metrics["Mean Squared Error"]
		datastudy_output[i,(2*assembly_kccs)+1:(3*assembly_kccs)+1]=eval_metrics["Root Mean Squared Error"]
		datastudy_output[i,(3*assembly_kccs)+1:(4*assembly_kccs)+1]=eval_metrics["R Squared"]

		file_name='metrics_data_study_'+str(train_dim)+'_.csv'
		accuracy_metrics_df.to_csv(logs_path+'/'+file_name)
		print("Model Training Complete on samples :",)
		print("The Model Validation Metrics are ")
		print(eval_metrics)
		K.clear_session()

	for i in range(len(eval_metrics_type)):
		datastudy_output[:,(4*assembly_kccs)+i+1]=np.mean(datastudy_output[:,(i*assembly_kccs)+1:((i+1)*assembly_kccs)+1],axis=1)

	#Gen Coloum Names

	col_names=['Training_Samples']
	for metric in eval_metrics_type:
		for kcc in kcc_id:
			col_names.append(str(metric)+'_'+str(kcc))

	for metric in eval_metrics_type:
	    col_names.append(str(metric)+"_avg")

	ds_output_df=pd.DataFrame(data=datastudy_output,columns=col_names)
	ds_output_df.to_csv(logs_path+'/'+'datastudy_output.csv')

	print('Data Study Completed Succssesfully')

	fig = ds_output_df.iplot(x='Training_Samples',asFigure=True)
	py.offline.plot(fig,filename=logs_path+'/'+"data_study_plot.html")
