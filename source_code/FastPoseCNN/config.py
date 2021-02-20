import os
import argparse
import pathlib

# Local imports
import tools

#-------------------------------------------------------------------------------
# Configurations

# Run hyperparameters
class DEFAULT_POSE_HPARAM(argparse.Namespace):
    
    # Experiment Identification 
    EXPERIMENT_NAME = "TESTING" # string
    DEBUG = False

    # Training Specifications
    #CHECKPOINT = pathlib.Path(os.getenv("LOGS")) / 'good_saved_runs' / '2_object' / '21-38-XY_REGRESSION_DEBUG-CAMERA-resnet18-imagenet' / '_' / 'checkpoints' / 'last.ckpt'
    CHECKPOINT = pathlib.Path(os.getenv("LOGS")) / 'good_saved_runs' / 'all_object' / '23-52-ALL_OBJECTS_E3-CAMERA-resnet18-imagenet' / '_' / 'checkpoints' / 'last.ckpt'
    DATASET_NAME = 'CAMERA' # string
    #SELECTED_CLASSES = ['bg','camera','laptop']
    SELECTED_CLASSES = tools.pj.constants.CAMERA_CLASSES 
    CKPT_SAVE_FREQUENCY = 5

    # Run Specifications
    CUDA_VISIBLE_DEVICES = '2,3' # '0,1,2,3'
    BATCH_SIZE = 2
    NUM_WORKERS = 18 # 36 total CPUs
    NUM_GPUS = 2 # 4 total GPUs
    TRAIN_SIZE= None#20#5000#100
    VALID_SIZE= None#10#300#20

    # Training Specifications
    WEIGHT_DECAY = 0.003
    LEARNING_RATE = 0.001
    ENCODER_LEARNING_RATE = 0.005
    NUM_EPOCHS = 50#2#50
    DISTRIBUTED_BACKEND = None if NUM_GPUS <= 1 else 'ddp'

    # Freezing Training Specifications
    FREEZE_ENCODER = False
    FREEZE_MASK_TRAINING = False
    FREEZE_ROTATION_TRAINING = False
    FREEZE_TRANSLATION_TRAINING = False
    FREEZE_SCALES_TRAINING = False

    # Algorithmic Training Specifications
    PERFORM_AGGREGATION = True
    PERFORM_HOUGH_VOTING = True
    PERFORM_RT_CALCULATION = True
    PERFORM_MATCHING = True

    # Architecture Parameters
    BACKBONE_ARCH = 'FPN'
    ENCODER = 'resnet18' #'resnext50_32x4d'
    ENCODER_WEIGHTS = 'imagenet'

    # Algorithmic Parameters
    
    ## Hough Voting Parameters 
    HV_NUM_OF_HYPOTHESES = 51 # Good at 50 though (preferably 2*n + 1 because of iqr)
    HV_HYPOTHESIS_IN_MASK_MULTIPLIER = 3 
    
    ### Pruning Parameters
    PRUN_METHOD = 'iqr' # options = (None, 'z-score', 'iqr')
    PRUN_OUTLIER_DROP = False
    PRUN_OUTLIER_REPLACEMENT_STYLE = 'median'

    ### Pruning Method Parameters (Z-score)
    PRUN_ZSCORE_THRESHOLD=1

    ### Pruning Method Parameters (IQR)
    IQR_MULTIPLIER=1.5