import pdb
import shutil
import os

import numpy as np

import torch
import torch.nn

import pytorch_lightning as pl
from pytorch_lightning.utilities import rank_zero_only

# Local Imports
import visualize

#-------------------------------------------------------------------------------
# Classes

class MyCallback(pl.callbacks.Callback):

    @rank_zero_only
    def __init__(self, hparams, tracked_data):
        super().__init__()

        self.hparams = hparams
        self.tracked_data = tracked_data

        max_metrics = {k:0 for k in self.tracked_data['maximize']}
        min_metrics = {k:np.inf for k in self.tracked_data['minimize']}
        
        self.metric_dict = max_metrics
        self.metric_dict.update(min_metrics)

    @rank_zero_only
    def on_train_epoch_end(self, trainer, pl_module):

        # Performing the shared functions of logging after end of epoch
        self.shared_epoch_end('train', trainer, pl_module)

    @rank_zero_only
    def on_validation_epoch_end(self, trainer, pl_module):

        # Performing the shared functions of logging after end of epoch
        self.shared_epoch_end('valid', trainer, pl_module)

    @rank_zero_only
    def shared_epoch_end(self, mode, trainer, pl_module):

        # Log the average for the metrics for each epoch
        self.log_epoch_average(mode, trainer, pl_module)

        # Log visualizatino of the mask
        self.log_epoch_mask(mode, trainer, pl_module)

    @rank_zero_only
    def log_epoch_average(self, mode, trainer, pl_module):

        log = pl_module.logger.log[mode]

        for log_name in log.keys():

            tb_log_name = log_name.replace('/batch', '')

            # if the log name is from the desired tensorboard metrics, then use it
            if tb_log_name in sum(self.tracked_data.values(), []):

                # Move all items inside the logger into cuda:0
                cuda_0_log = [x.to('cuda:0') for x in log[log_name]]

                # Obtain the average first
                average = torch.mean(torch.stack(cuda_0_log))

                # Log the average
                trainer.logger.log_metrics(
                    mode, 
                    {f'{tb_log_name}/epoch': average},
                    trainer.current_epoch+1,
                    store=False
                )

                # Save the best value (epoch level) to later log into hparams
                # If maximize, take the maximum value
                if tb_log_name in self.tracked_data['maximize']:
                    if self.metric_dict[tb_log_name] < average:
                        self.metric_dict[tb_log_name] = average
                
                # If minimize, take the minimum value
                elif tb_log_name in self.tracked_data['minimize']:
                    if self.metric_dict[tb_log_name] > average:
                        self.metric_dict[tb_log_name] = average    

        # After an epoch, we clear out the log
        pl_module.logger.clear_metrics(mode)
        
    @rank_zero_only
    def log_epoch_mask(self, mode, trainer, pl_module):

        # Obtaining the LightningDataModule
        datamodule = trainer.datamodule

        # Accessing the corresponding dataset
        dataset = datamodule.datasets[mode]

        # Obtaining the corresponding colormap from the dataset
        colormap = dataset.COLORMAP

        # Get random sample
        sample = dataset.get_random_batched_sample(batch_size=3)

        # Create the summary figure
        summary_fig = self.mask_check_tb(sample, pl_module, colormap)

        # Log the figure to tensorboard
        pl_module.logger.writers[mode].add_figure(f'mask_gen/{mode}', summary_fig, trainer.global_step)

    @rank_zero_only
    def mask_check_tb(self, sample, pl_module, colormap):

        #pdb.set_trace()

        # Selecting clean image and mask if available
        image_key = 'clean image' if 'clean image' in sample.keys() else 'image'
        mask_key = 'clean mask' if 'clean mask' in sample.keys() else 'mask'
        
        image_vis = sample[image_key].astype(np.uint8)
        gt_mask = sample[mask_key].astype(np.uint8)

        #pdb.set_trace()
        
        # Given the sample, make the prediction with the PyTorch Lightning Module
        logits = pl_module(torch.from_numpy(sample['image']).float().to(pl_module.device)).detach()
        pr_mask = torch.nn.functional.sigmoid(logits).cpu().numpy()

        #pdb.set_trace()

        # Target (ground truth) data format 
        if len(gt_mask.shape) == len('BCHW'):

            if pr_mask.shape[1] == 1: # Binary segmentation
                pr_mask = pr_mask[:,0,:,:]
                gt_mask = gt_mask[:,0,:,:]

            else: # Multi-class segmentation
                pr_mask = np.argmax(pr_mask, axis=1)
                gt_mask = np.argmax(gt_mask, axis=1)

        elif len(gt_mask.shape) == len('BHW'):

            if pr_mask.shape[1] == 1: # Binary segmentation
                pr_mask = pr_mask[:,0,:,:]

            else: # Multi-class segmentation
                pr_mask = np.argmax(pr_mask, axis=1)

        # Colorized the binary masks
        #pdb.set_trace()

        gt_mask_vis = visualize.get_visualized_masks(gt_mask, colormap)
        pr_mask = visualize.get_visualized_masks(pr_mask, colormap)

        # Creating a matplotlib figure illustrating the inputs vs outputs
        summary_fig = visualize.make_summary_figure(
            image=image_vis,
            ground_truth_mask=gt_mask_vis,
            predicited_mask=pr_mask)

        #pdb.set_trace()

        return summary_fig

    @rank_zero_only
    def teardown(self, trainer, pl_module, stage):
        
        """
        # Log hyper parameters:
            - Using the initialization parameter self.hparams, we use that as the
              hparam_dict while the logger will contain the metrics_dict.
        """
        pl_module.logger.writers['base'].add_hparams(
            hparam_dict=self.hparams,
            metric_dict=self.metric_dict
        )

        # Remove the additional folder for this hyperparameter entry
        base_log_dir = pl_module.logger.base_dir

        # For all the items inside the base_log_dir of the run
        for child in base_log_dir.iterdir():

            # If the child is a directory
            if child.is_dir():

                # Take all the files out into the log_dir
                for file_in_child in child.iterdir():
                    shutil.move(str(file_in_child), str(base_log_dir))

                # Then delete the ugly folder >:(
                os.rmdir(str(child))