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
    DETERMINISTIC = False

    # Training Specifications
    #CHECKPOINT = None
    #CHECKPOINT = pathlib.Path(os.getenv("LOGS")) / 'good_saved_runs' / '2_object' / '21-38-XY_REGRESSION_DEBUG-CAMERA-resnet18-imagenet' / '_' / 'checkpoints' / 'last.ckpt'
    CHECKPOINT = pathlib.Path(os.getenv("LOGS")) / 'good_saved_runs' / 'all_object' / '22-10-LONG_MASK_ALL_OBJECTS-CAMERA-resnet18-imagenet' / '_' / 'checkpoints' / 'last.ckpt'
    #CHECKPOINT = pathlib.Path(os.getenv("LOGS")) / 'debugging_test_runs' / '13-15-MASK_TEST-CAMERA-resnet18-imagenet' / '_' / 'checkpoints' / 'n-ckpt_epoch=5.ckpt'
    #CHECKPOINT = pathlib.Path('/home/students/edavalos/GitHub/FastPoseCNN/source_code/FastPoseCNN/logs/21-03-11/08-30-HEAD_TRAINING2-Experimental-CAMERA-resnet18-imagenet/_/checkpoints/epoch=04-checkpoint_on=0.7862.ckpt')

    MODEL = 'PoseRegressor'
    DATASET_NAME = 'CAMERA' # string
    #SELECTED_CLASSES = ['bg','camera','laptop']
    SELECTED_CLASSES = tools.pj.constants.CAMERA_CLASSES 
    CKPT_SAVE_FREQUENCY = 5

    # Run Specifications
    CUDA_VISIBLE_DEVICES = '2' # '0,1,2,3'
    BATCH_SIZE = 2
    NUM_WORKERS = int(1 * (36/4)) # 36 total CPUs
    NUM_GPUS = 1 # 4 total GPUs
    
    # Test Trim Dataset
    # TRAIN_SIZE = 100
    # VALID_SIZE = 20

    # Small Trim Dataset
    # TRAIN_SIZE = 5_000
    # VALID_SIZE = 200

    # Large Trim Dataset
    TRAIN_SIZE = 10_000
    VALID_SIZE = 500

    # Entire Dataset
    # TRAIN_SIZE = None
    # VALID_SIZE = None

    # Training Specifications
    WEIGHT_DECAY = 0.0003
    LEARNING_RATE = 0.0001 / 10
    ENCODER_LEARNING_RATE = 0.00005 / 10
    NUM_EPOCHS = 50 #50
    DISTRIBUTED_BACKEND = None if NUM_GPUS <= 1 else 'ddp'

    # Loss Function Specifications
    MASK_WEIGHT = 0.1
    QUAT_WEIGHT = 0.1
    XY_WEIGHT = 0.1
    Z_WEIGHT = 0.1
    SCALES = 0.1

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

class MASK_TRAINING(DEFAULT_POSE_HPARAM):

    FREEZE_ENCODER = False
    FREEZE_MASK_TRAINING = False
    FREEZE_ROTATION_TRAINING = True
    FREEZE_TRANSLATION_TRAINING = True
    FREEZE_SCALES_TRAINING = True

    PERFORM_AGGREGATION = False 
    PERFORM_HOUGH_VOTING = False
    PERFORM_RT_CALCULATION = False
    PERFORM_MATCHING = False

class HEAD_TRAINING(DEFAULT_POSE_HPARAM):

    FREEZE_ENCODER = True
    FREEZE_MASK_TRAINING = True
    FREEZE_ROTATION_TRAINING = False
    FREEZE_TRANSLATION_TRAINING = False
    FREEZE_SCALES_TRAINING = False

    PERFORM_AGGREGATION = True
    PERFORM_HOUGH_VOTING = True
    PERFORM_RT_CALCULATION = True
    PERFORM_MATCHING = True