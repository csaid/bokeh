import numpy as np
import math
from ..objects import ServerDataSource

def source(domain='x', method='minmax', **kwargs):
  kwargs['transform'] = {'resample':'line1d', 'domain':domain, 'method':method}
  return ServerDataSource(**kwargs)


def downsample(data,
               domain_column,
               primary_data_column,
               domain_limit, 
               domain_resolution, 
               method):
    """
    data : record numpy array of values, shape (N,)
    domain_column : column index representing the domain of the plot
    primary_data_column : column index of data that is used for
    min/max decimation
    domain_limit : bounds of domain (tuple of length 2)
    domain_resolution : # of samples
    method : 'maxmin' encodes the max/min point. 
             'mid' encode the midpoint of each bin-range 
    
    output:
    list of (domain,data) pairs, where they are each 1d vectors
    """
    #sort data
    indexes = np.argsort(data[domain_column])
    data = data[indexes]
    
    #truncate data based on domain_limits
    domain = data[domain_column]
    left_idx = np.searchsorted(domain, domain_limit[0], side='left')
    right_idx = np.searchsorted(domain, domain_limit[1], side='right')
    data = data[left_idx:right_idx + 1]
    
    domain = data[domain_column]
    bucket_size = (domain_limit[1] - domain_limit[0]) / domain_resolution
    buckets = (domain - domain.min()) / bucket_size
    buckets = np.floor(buckets)
    starting_boundaries = np.searchsorted(buckets, 
                                          np.unique(buckets), 
                                          side='left').tolist()
    ending_boundaries = starting_boundaries[1:]
    ending_boundaries.append(None)
    if len(starting_boundaries) * 2 > len(data):
        return data

    downsampled_data = []
    for st, ed in zip(starting_boundaries, ending_boundaries):
        subdata = data[st:ed]
        if subdata.shape[0] == 0:
            continue
        
        primary_column = subdata[primary_data_column]
        idx = np.argsort(primary_column)
        #downsample
        if (method == 'minmax'):
          min_idx = idx[0]
          max_idx = idx[-1]
          subdata = subdata[[min_idx, max_idx]]
        elif (method == 'mid'):
          mid_idx = idx[len(idx)/2]
          part = subdata[[mid_idx]]
        else :
          raise ValueError("Line downsample method not known: " + method)
        downsampled_data.append(subdata)

    downsampled_data = np.concatenate(downsampled_data)
    #resort data
    indexes = np.argsort(downsampled_data[domain_column])
    downsampled_data = downsampled_data[indexes]
    return downsampled_data
