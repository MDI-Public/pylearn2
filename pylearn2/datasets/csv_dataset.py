# -*- coding: utf-8 -*-
"""
A simple general csv dataset wrapper for pylearn2.
Can do automatic one-hot encoding based on labels present in a file.
"""
__authors__ = "Zygmunt Zając"
__copyright__ = "Copyright 2013, Zygmunt Zając"
__credits__ = ["Zygmunt Zając", "Nicholas Dronen"]
__license__ = "3-clause BSD"
__maintainer__ = "?"
__email__ = "zygmunt@fastml.com"

import csv
import numpy as np
import os

from pylearn2.datasets.dense_design_matrix import DenseDesignMatrix
from pylearn2.utils import serial
from pylearn2.utils.string_utils import preprocess


class CSVDataset(DenseDesignMatrix):
    """
    A generic class for accessing CSV files
    labels, if present, should be in the first column
    if there's no labels, set expect_labels to False
    if there's no header line in your file, set expect_headers to False

    Parameters
    ----------
    path : WRITEME
    one_hot : WRITEME
    expect_labels : WRITEME
    expect_headers : WRITEME
    delimiter : WRITEME
    start : WRITEME
    stop : WRITEME
    """

    def __init__(self, 
            path = 'train.csv',
            one_hot = False,
            expect_labels = True,
            expect_headers = True,
            delimiter = ',',
            start = None,
            stop = None,
            start_fraction = None,
            end_fraction = None):
        """
        .. todo::

            WRITEME
        """
        self.path = path
        self.one_hot = one_hot
        self.expect_labels = expect_labels
        self.expect_headers = expect_headers
        self.delimiter = delimiter
        self.start = start
        self.stop = stop
        self.start_fraction = start_fraction
        self.end_fraction = end_fraction
        
        self.view_converter = None

        if start_fraction is not None:
            if end_fraction is not None:
                raise ValueError("Use start_fraction or end_fraction, " +
                        " just not both.")
            if start_fraction <= 0:
                raise ValueError("start_fraction should be > 0")

            if start_fraction >= 1:
                raise ValueError("start_fraction should be < 1")

        if end_fraction is not None:
            if end_fraction <= 0:
                raise ValueError("end_fraction should be > 0")

            if end_fraction >= 1:
                raise ValueError("end_fraction should be < 1")



        if start is not None:
            if start_fraction is not None or end_fraction is not None:
                raise ValueError("Use start, start_fraction, or end_fraction," +
                        " just not together.")

        if stop is not None:
            if start_fraction is not None or end_fraction is not None:
                raise ValueError("Use stop, start_fraction, or end_fraction," +
                        " just not together.")

        # and go

        self.path = preprocess(self.path)
        X, y = self._load_data()
        
        super(CSVDataset, self).__init__(X=X, y=y)

    def _load_data(self):
        """
        .. todo::

            WRITEME
        """
        assert self.path.endswith('.csv')
    
        if self.expect_headers:
            data = np.loadtxt(self.path, delimiter = self.delimiter, skiprows = 1)
        else:
            data = np.loadtxt(self.path, delimiter = self.delimiter)

        def take_subset(X, y):
            if self.start_fraction is not None:
                n = X.shape[0]
                subset_end = int(self.start_fraction * n)
                X = X[0:subset_end, :]
                y = y[0:subset_end]
            elif self.end_fraction is not None:
                n = X.shape[0]
                subset_start = int((1-self.end_fraction) * n)
                X = X[subset_start:, ]
                y = y[subset_start:]
            elif self.start is not None:
                if self.stop is None:
                    X = X[self.start:, ]
                    if y is not None:
                        y = y[self.start:]
                else:
                    X = X[self.start:self.stop, ]
                    if y is not None:
                        y = y[self.start:self.stop]

            return X, y
        
        if self.expect_labels:
            y = data[:,0]
            X = data[:,1:]
            
            # get unique labels and map them to one-hot positions
            labels = np.unique(y)
            labels = dict((x, i) for (i, x) in enumerate(labels))

            if self.one_hot:
                one_hot = np.zeros((y.shape[0], len(labels)), dtype='float32')
                for i in xrange(y.shape[0]):
                    label = y[i]
                    label_position = labels[label]
                    one_hot[i,label_position] = 1.
                y = one_hot
            else:
                y = y.reshape((y.shape[0], 1))

        else:
            X = data
            y = None

        X, y = take_subset(X, y)

        return X, y
