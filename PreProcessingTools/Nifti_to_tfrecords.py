__author__ = 'Brian M Anderson'
# Created on 11/18/2020

from Base_Deeplearning_Code.Make_Single_Images.Make_TFRecord_Class import write_tf_record
from Base_Deeplearning_Code.Image_Processors_Module.src.Processors import MakeTFRecordProcessors as Processors
Processors.LoadNifti(nifti_path_keys=('image_path', 'annotation_path'), out_keys=('image_handle', 'annotation_handle'))

def path_parser(niftii_path, **kwargs):
    data_dict = {}
    primary_files = [i for i in os.listdir(niftii_path) if i.endswith('_Primary_Dicom.nii')]
    for file in primary_files:
        iteration = file.split('_')[0]
        data_dict[iteration] = {'primary_image_path': os.path.join(niftii_path, file),
                                'primary_mask_path': os.path.join(niftii_path, file.replace('Dicom', 'Mask')),
                                'secondary_image_path': os.path.join(niftii_path, file.replace('Primary', 'Secondary')),
                                'secondary_deformed_path': os.path.join(niftii_path, file.replace('Primary_Dicom',
                                                                                                  'Secondary_Deformed')),
                                'secondary_mask_path': os.path.join(niftii_path, file.replace('Primary_Dicom',
                                                                                              'Secondary_Mask')),
                                'file_name': '{}.tfrecord'.format(file.split('_')[0])
                                }
    return data_dict


def nifti_to_records(nifti_path):
    """
    :param nifti_path: path to the nifti files
    :return:
    """
    Contour_names = ['Retro_GTV', 'Retro_GTV_Recurred', 'Liver']  # Just a note for key value listing
    base_normalizer = [
        Add_Images_And_Annotations(nifti_path_keys=('primary_image_path', 'secondary_image_path',
                                                    'primary_mask_path', 'secondary_mask_path',
                                                    'secondary_deformed_path'),
                                   out_keys=('primary_image', 'secondary_image', 'primary_mask',
                                             'secondary_mask', 'secondary_image_deformed'),
                                   dtypes=('float32', 'float32', 'int8', 'int8', 'float32')),
        Resampler(resample_keys=('primary_image', 'secondary_image', 'secondary_image_deformed', 'primary_mask',
                                 'secondary_mask'),
                  desired_output_spacing=(1., 1., 2.5),
                  resample_interpolators=('Linear', 'Linear', 'Linear', 'Nearest', 'Nearest')),
        Processors.Threshold_Images(image_keys=('image_array',), lower_bound=-100, upper_bound=200),
        Threshold_Images(image_key='secondary_image', lower_bound=-200, upper_bound=200, divide=False),
        Threshold_Images(image_key='secondary_image_deformed', lower_bound=-200, upper_bound=200, divide=False),
        Normalize_to_annotation(image_key='primary_image', annotation_key='primary_mask',
                                annotation_value_list=[1, 2, 3], mirror_max=True),
        Normalize_to_annotation(image_key='secondary_image', annotation_key='secondary_mask',
                                annotation_value_list=[1], mirror_max=True),
        Normalize_to_annotation(image_key='secondary_image_deformed', annotation_key='primary_mask',
                                annotation_value_list=[1, 2, 3], mirror_max=True),
        Threshold_Images(image_key='primary_image', lower_bound=-15, upper_bound=10, divide=False),
        Threshold_Images(image_key='secondary_image', lower_bound=-15, upper_bound=10, divide=False),
        Threshold_Images(image_key='secondary_image_deformed', lower_bound=-15, upper_bound=10, divide=False),
        AddByValues(image_keys=('primary_image', 'secondary_image', 'secondary_image_deformed'),
                    values=(2.5, 2.5, 2.5)),
        DivideByValues(image_keys=('primary_image', 'secondary_image', 'secondary_image_deformed'),
                       values=(12.5, 12.5, 12.5)),
        DistributeIntoRecurrenceCubes(images=32, rows=64, cols=64)
    ]
    write_tf_record(niftii_path=nifti_path, file_parser=path_parser, max_records=np.inf,
                    out_path=os.path.join(nifti_path, 'Records'),
                    recordwriter=RecordWriterRecurrence(out_path=os.path.join(nifti_path, 'Records'),
                                                        file_name_key='file_name', rewrite=True),
                    image_processors=base_normalizer, is_3D=True, thread_count=20, debug=False)


if __name__ == '__main__':
    pass
