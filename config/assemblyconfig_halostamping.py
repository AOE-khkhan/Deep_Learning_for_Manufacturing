
assembly_system = {	
        'data_type': '3D Point Cloud Data',
        'application': 'Inline Root Cause Analysis',
        'part_type': 'Halo_debug_run',
        'part_name':'Halo',
        'data_format': 'Complete',
        'assembly_type':"Single-Stage",
        'assembly_kccs':3,
        'assembly_kpis':1,
        'voxel_dim':64,
        'point_dim':8047,
        'voxel_channels':3,
        'system_noise':0.0,
        'aritifical_noise':0.0,
        'noise_type':'uniform',
        'mapping_index':'Halo_64_voxel_mapping.dat',
        'data_folder':'../datasets/halo_debug_run/',
        'kcc_folder':'../active_learning/sample_input/',
        'kcc_files':['initial_samples_train_set.csv'],
        'test_kcc_files':['initial_samples_test_set.csv'],
        'data_files_x':['output_table_x_test_set.csv'],
        'data_files_y':['output_table_y_test_set.csv'],
        'data_files_z':['output_table_z_test_set.csv'],
        'test_data_files_x':['output_table_x_test_set.csv'],
        'test_data_files_y':['output_table_y_test_set.csv'],
        'test_data_files_z':['output_table_x_test_set.csv']
        }

#Assert that all config values conform to the libarary requirements
assert type(assembly_system['assembly_kccs']) is int, "Assembly KCCs is not an integer: %r" %assembly_system[assembly_kccs]
assert type(assembly_system['assembly_kpis']) is int, "Assembly KPIs is not an integer: %r" % assembly_system[assembly_kpis]
assert type(assembly_system['voxel_dim']) is int, "Voxel Dim is not an integer: %r" % assembly_system[voxel_dim]
assert type(assembly_system['point_dim']) is int, "Point Dim is not an integer: %r" % assembly_system[point_dim]
assert type(assembly_system['voxel_channels']) is int, "Voxel Channels is not an integer: %r" % assembly_system[voxel_channels]
assert type(assembly_system['system_noise']) is float, "Noise Level is not float: %r" % assembly_system[noise_levels]
