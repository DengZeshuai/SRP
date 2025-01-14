import argparse
import template
import glob
from smilelogging import argparser as parser
from smilelogging.utils import strlist_to_list, strdict_to_dict, check_path, parse_prune_ratio_vgg

# parser = argparse.ArgumentParser(description='EDSR and MDSR')

# parser.add_argument('--debug', action='store_true',
#                     help='Enables debug mode') # @mst: Avoid re-definition because --debug has been used in smilelogging args
parser.add_argument('--template', default='.',
                    help='You can set various templates in option.py')

# Hardware specifications
parser.add_argument('--n_threads', type=int, default=6,
                    help='number of threads for data loading')
parser.add_argument('--cpu', action='store_true',
                    help='use cpu only')
parser.add_argument('--n_GPUs', type=int, default=1,
                    help='number of GPUs')
parser.add_argument('--seed', type=int, default=1,
                    help='random seed')

# Data specifications
parser.add_argument('--dir_data', type=str, default='/mnt/cephfs/dataset/sr',
                    help='dataset directory')
parser.add_argument('--dir_demo', type=str, default='../test',
                    help='demo image directory')
parser.add_argument('--data_train', type=str, default='DF2K',
                    help='train dataset name')
parser.add_argument('--data_test', type=str, default='Set5',
                    help='test dataset name')
parser.add_argument('--data_range', type=str, default='1-3550/3551-3555',
                    help='train/test data range')
parser.add_argument('--ext', type=str, default='img',
                    help='dataset file extension')
parser.add_argument('--scale', type=str, default='4',
                    help='super resolution scale')
parser.add_argument('--patch_size', type=int, default=192,
                    help='output patch size')
parser.add_argument('--rgb_range', type=int, default=255,
                    help='maximum value of RGB')
parser.add_argument('--n_colors', type=int, default=3,
                    help='number of color channels to use')
parser.add_argument('--chop', action='store_true',
                    help='enable memory-efficient forward')
parser.add_argument('--no_augment', action='store_true',
                    help='do not use data augmentation')

# Model specifications
parser.add_argument('--model', default='EDSR',
                    help='model name')

parser.add_argument('--act', type=str, default='relu',
                    help='activation function')
parser.add_argument('--pre_train', type=str, default='',
                    help='pre-trained model directory')
parser.add_argument('--extend', type=str, default='.',
                    help='pre-trained model directory')
parser.add_argument('--n_resblocks', type=int, default=16,
                    help='number of residual blocks')
parser.add_argument('--n_feats', type=int, default=64,
                    help='number of feature maps')
parser.add_argument('--res_scale', type=float, default=1,
                    help='residual scaling')
parser.add_argument('--shift_mean', default=True,
                    help='subtract pixel mean from the input')
parser.add_argument('--dilation', action='store_true',
                    help='use dilated convolution')
parser.add_argument('--precision', type=str, default='single',
                    choices=('single', 'half'),
                    help='FP precision for test (single | half)')

# Option for Residual dense network (RDN)
parser.add_argument('--G0', type=int, default=64,
                    help='default number of filters. (Use in RDN)')
parser.add_argument('--RDNkSize', type=int, default=3,
                    help='default kernel size. (Use in RDN)')
parser.add_argument('--RDNconfig', type=str, default='B',
                    help='parameters config of RDN. (Use in RDN)')

# Option for Residual channel attention network (RCAN)
parser.add_argument('--n_resgroups', type=int, default=10,
                    help='number of residual groups')
parser.add_argument('--reduction', type=int, default=16,
                    help='number of feature maps reduction')

# Training specifications
parser.add_argument('--reset', action='store_true',
                    help='reset the training')
parser.add_argument('--test_every', type=int, default=1000,
                    help='do test per every N batches')
parser.add_argument('--epochs', type=int, default=5000,
                    help='number of epochs to train')
parser.add_argument('--batch_size', type=int, default=16,
                    help='input batch size for training')
parser.add_argument('--split_batch', type=int, default=1,
                    help='split the batch into smaller chunks')
parser.add_argument('--self_ensemble', action='store_true',
                    help='use self-ensemble method for test')
parser.add_argument('--test_only', action='store_true',
                    help='set this option to test the model')
parser.add_argument('--gan_k', type=int, default=1,
                    help='k value for adversarial loss')

# Optimization specifications
parser.add_argument('--lr', type=float, default=1e-4,
                    help='learning rate')
parser.add_argument('--lr_decay', type=int, default=200,
                    help='learning rate decay per N epochs')
parser.add_argument('--decay_type', type=str, default='step',
                    help='learning rate decay type') 
parser.add_argument('--decay', type=str, default='200',
                    help='learning rate decay type, multiple_step, 200-400-600-800-1000')
parser.add_argument('--gamma', type=float, default=0.5,
                    help='learning rate decay factor for step decay')
parser.add_argument('--T_0', type=int, default=250,
                    help='T_0 in CosineAnnealingWarmRestarts')
parser.add_argument('--optimizer', default='ADAM',
                    choices=('SGD', 'ADAM', 'RMSprop'),
                    help='optimizer to use (SGD | ADAM | RMSprop)')
parser.add_argument('--momentum', type=float, default=0.9,
                    help='SGD momentum')
parser.add_argument('--betas', type=tuple, default=(0.9, 0.999),
                    help='ADAM beta')
parser.add_argument('--epsilon', type=float, default=1e-8,
                    help='ADAM epsilon for numerical stability')
parser.add_argument('--weight_decay', type=float, default=0,
                    help='weight decay')
parser.add_argument('--gclip', type=float, default=0,
                    help='gradient clipping threshold (0 = no clipping)')

# Loss specifications
parser.add_argument('--loss', type=str, default='1*L1',
                    help='loss function configuration')
parser.add_argument('--skip_threshold', type=float, default='1e8',
                    help='skipping batch that has large error')

# Log specifications
parser.add_argument('--save', type=str, default='test',
                    help='file name to save')
parser.add_argument('--load', type=str, default='',
                    help='file name to load')
parser.add_argument('--resume', type=int, default=0,
                    help='resume from specific checkpoint')
parser.add_argument('--save_models', action='store_true',
                    help='save all intermediate models')
parser.add_argument('--only_keep_minlrate_models', action='store_true',
                    help='only keep the min lrate models')
parser.add_argument('--print_every', type=int, default=100,
                    help='how many batches to wait before logging training status')
parser.add_argument('--save_results', action='store_true',
                    help='save output results')
parser.add_argument('--save_gt', action='store_true',
                    help='save low-resolution and high-resolution images together')

# Lightweight SR
parser.add_argument('--method', type=str, default='', choices=['', 'SRP'], help='method name')
parser.add_argument('--wg', type=str, default='filter', choices=['filter', 'weight'], help='weight group to prune')
parser.add_argument('--stage_pr', type=str, default="", help='to appoint layer-wise pruning ratio')
parser.add_argument('--kr_mul', type=float, default=1, help='multiplier for kept ratio')
parser.add_argument('--reg_select_stop_pr', type=float, default=-1, help='the pr threshold that decides if PruneSelect is finished')
parser.add_argument('--index_layer', type=str, default="number", choices=['number', 'name_matching'])
parser.add_argument('--skip_layers', type=str, default="",  help='layers to skip when pruning')
parser.add_argument('--reinit_layers', type=str, default="", help='layers to reinit (not inherit weights)')
parser.add_argument('--same_pruned_wg_layers', type=str, default='', help='layers to be set with the same pruned weight group')
parser.add_argument('--same_pruned_wg_criterion', type=str, default='rand', choices=['rand', 'reg'], help='use which criterion to select pruned wg')
parser.add_argument('--num_layers', type=int, default=100, help='num of layers in the network')
parser.add_argument('--resume_path', type=str, default='', help='path of the checkpoint to resume')

# SRP
parser.add_argument('--print_interval', type=int, default=100)
parser.add_argument('--update_reg_interval', type=int, default=20)
parser.add_argument('--stabilize_reg_interval', type=int, default=43150)
parser.add_argument('--reg_upper_limit', type=float, default=0.5)
parser.add_argument('--reg_granularity_prune', type=float, default=1e-4)
parser.add_argument('--pick_pruned', type=str, default='min', choices=['min', 'max', 'rand'])
parser.add_argument('--not_apply_reg', dest='apply_reg', action='store_false', default=True)
parser.add_argument('--layer_chl', type=str, default='', help='manually assign the number of channels for some layers. A not so beautiful scheme.')
parser.add_argument('--greg_mode', type=str, default='part', choices=['part', 'all'])
parser.add_argument('--compare_mode', type=str, default='local', choices=['local', 'global'])
parser.add_argument('--prune_criterion', type=str, default='l1-norm', choices=['l1-norm'])
parser.add_argument('--wn', action='store_true', help='if use weight normalization')
parser.add_argument('--lw_spr', type=float, default=1, help='lw for loss of sparsity pattern regularization')
parser.add_argument('--iter_finish_spr', '--iter_ssa', dest='iter_ssa', type=int, default=17260, help='863x20 = 20 epochs')
parser.add_argument('--lr_prune', type=float, default=1e-4)
parser.add_argument('--freeze_skip_layers', action='store_true')
parser.add_argument('--constrained_sparsity', type=float, default=-1)
parser.add_argument('--total_sparsity', type=float, default=-1)
parser.add_argument('--save_mag_reg_log', action='store_true')

args = parser.parse_args()
template.set_template(args)

args.scale = list(map(lambda x: int(x), args.scale.split('+')))
args.data_train = args.data_train.split('+')
args.data_test = args.data_test.split('+')

if args.epochs == 0:
    args.epochs = 1e8

for arg in vars(args):
    if vars(args)[arg] == 'True':
        vars(args)[arg] = True
    elif vars(args)[arg] == 'False':
        vars(args)[arg] = False

# parse for layer-wise prune ratio
# stage_pr is a list of float, skip_layers is a list of strings
if args.method in ['SRP']:
    assert args.stage_pr
    if ',,,' in args.stage_pr: # ',,,' is seperator
        base_pr_model, rest = args.stage_pr.split(',,,')
    else:
        base_pr_model = args.stage_pr
    
    if glob.glob(base_pr_model): # 'stage_pr' is a path
        rest = f',,,{rest}' if ',,,' in args.stage_pr else ''
        args.stage_pr = check_path(base_pr_model) + rest
    
    else:
        if args.compare_mode in ['global']: # 'stage_pr' is a float
            args.stage_pr = float(args.stage_pr)
        
        elif args.compare_mode in ['local']: # 'stage_pr' is a list
            if args.index_layer in ['number']:
                args.stage_pr = parse_prune_ratio_vgg(args.stage_pr, num_layers=args.num_layers)
            elif args.index_layer in ['name_matching']:
                args.stage_pr = strdict_to_dict(args.stage_pr, float)
            else:
                raise NotImplementedError
            
    args.skip_layers = strlist_to_list(args.skip_layers, str)
    args.reinit_layers = strlist_to_list(args.reinit_layers, str)
    args.same_pruned_wg_layers = strlist_to_list(args.same_pruned_wg_layers, str)
    args.layer_chl = strdict_to_dict(args.layer_chl, int)

# directly appoint some values to maintain compatibility
args.reinit = False