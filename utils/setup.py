import torch
import numpy as np
import utils.dnnlib as dnnlib

def worker_init_fn(worker_id):
    st=np.random.get_state()[2]
    np.random.seed( st+ worker_id)


def setup_dataset(args):
    #the dataloader loads audio at the original sampling rate, then in the training loop we resample it to the target sampling rate. The mismatch between sampling rates is indicated by the resample_factor
    if args.dset.name=="maestro_allyears":
            dataset_obj=dnnlib.call_func_by_name(func_name=args.dset.callable, dset_args=args.dset)
    elif args.dset.name=="singing_voice":
            dataset_obj=dnnlib.call_func_by_name(func_name=args.dset.callable, dset_args=args.dset)
    else:
            dataset_obj=dnnlib.call_func_by_name(func_name=args.dset.callable, dset_args=args.dset, fs=args.exp.sample_rate*args.exp.resample_factor, seg_len=args.exp.audio_len*args.exp.resample_factor)
            
        
    dataset_iterator = iter(torch.utils.data.DataLoader(dataset=dataset_obj, batch_size=args.exp.batch,  num_workers=args.exp.num_workers, pin_memory=True, worker_init_fn=worker_init_fn, timeout=0, prefetch_factor=20))
        
    return dataset_iterator

def setup_dataset_test(args):

    if args.dset.name=="maestro_allyears" or args.dset.name=="maestro_fs":
        dataset_obj=dnnlib.call_func_by_name(func_name=args.dset.test.callable, dset_args=args.dset, num_samples=args.dset.test.num_samples)
    else:
        dataset_obj=dnnlib.call_func_by_name(func_name=args.dset.test.callable, dset_args=args.dset, fs=args.exp.sample_rate,seg_len=args.exp.audio_len, num_samples=args.dset.test.num_samples)
    
    dataset = torch.utils.data.DataLoader(dataset=dataset_obj, batch_size=args.dset.test.batch_size,  num_workers=args.exp.num_workers, pin_memory=True, worker_init_fn=worker_init_fn)

    return dataset

def setup_diff_parameters(args):

    diff_params_obj=dnnlib.call_func_by_name(func_name=args.diff_params.callable, args=args)

    return diff_params_obj

def setup_network(args, device, operator=False):
        network_obj=dnnlib.call_func_by_name(func_name=args.network.callable, args=args, device=device)

        return network_obj.to(device)

def setup_denoiser(args, device):

        network_obj=dnnlib.call_func_by_name(func_name=args.tester.denoiser.callable, unet_args=args.tester.denoiser)

        return network_obj.to(device)

def setup_optimizer(args, network):
    # setuo optimizer for training
    optimizer = torch.optim.Adam(network.parameters(), lr=args.exp.lr, betas=(args.exp.optimizer.beta1, args.exp.optimizer.beta2), eps=args.exp.optimizer.eps)
    return optimizer

def setup_tester(args, network=None, diff_params=None,  device="cpu"):
    assert network is not None
    assert diff_params is not None
    if args.tester.do_test:
        # setuo sampler for making demos during training
        sampler = dnnlib.call_func_by_name(func_name=args.tester.callable, args=args, network=network,  diff_params=diff_params, device=device)
        return sampler
    else:
        return None

def setup_trainer(args, dset=None, network=None, optimizer=None, diff_params=None, tester=None, device="cpu"):
    assert network is not None
    assert diff_params is not None
    assert optimizer is not None
    assert tester is not None
    print(args.exp.trainer_callable)
    trainer = dnnlib.call_func_by_name(func_name=args.exp.trainer_callable, args=args, dset=dset, network=network, optimizer=optimizer, diff_params=diff_params, tester=tester, device=device)
    return trainer
    

    




