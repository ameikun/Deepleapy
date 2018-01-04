import numpy as np

def zero_pad(X,pad):
    """
    Pad with zeros all images of the dataset X. The padding is applied to
    the height and width of an image
    Parameters
    ----------
    X : python numpy array of shape (m, n_H, n_W, n_C)
        representing a batch of m images
    pad : integer
        amount of padding around each image on vertical and horizontal dimensions

    Returns:
    -------
        padded image of shape (m, n_H + 2*pad, n_W + 2*pad, n_C)
    """
    if X.ndim == 2:
        X = np.pad(X, ((pad, pad),(pad, pad)), 'constant',constant_values=(0,0))
    if X.ndim == 3:
        X = np.pad(X, ((pad, pad),(pad, pad),(0,0)), 'constant',constant_values=(0,0))
    if X.ndim == 4:
        X = np.pad(X, ((0,0),(pad, pad),(pad, pad),(0,0)), 'constant',constant_values=(0,0))

    return X

def conv(X,W,b,hyperparams):
    """
    Implements the forward propagation for a convolution function
    Parameters
    ----------
    A_prev : numpy array of shape (m, n_H_prev, n_W_prev, n_C_prev)
        output activations of the previous layer
    W : numpy array of shape (f, f, n_C_prev, n_C)
        Weights
    b : numpy array of shape (1, 1, n_C)
        Biases
    hparameters -- python dictionary containing "stride" and "pad"
    Returns:
    -------
    Z : conv output, numpy array of shape (m, n_H, n_W, n_C)
    cache -- cache of values needed for the conv_backward() function
    """
    pad=hyperparams['conv_pad']
    stride=hyperparams['conv_stride']
    filter_size = W.shape[0]
    m = X.shape[0]
    outh = 1 + int( ( X.shape[1] - filter_size + 2*pad ) / stride )
    outw = 1 + int( ( X.shape[2] - filter_size + 2*pad ) / stride )
    outl = W.shape[3]
    # pad X with zeros
    X = zero_pad(X, pad)
    # the number of output layers
    res = np.zeros((m,outh,outw,outl))
    for i in range(m):
        sample = X[i]
        for h in range(outh):
            for w in range(outw):
                for l in range(outl):
                    starth = h * stride
                    endh = starth + filter_size
                    startw = w * stride
                    endw = startw + filter_size
                    res[i,h,w,l] = np.sum( sample[starth:endh,startw:endw] * W[:,:,:,l] + b[:,:,:,l])

    return res

def pool_forward(A_prev, hyperparams):
    """
    Implements the forward pass of the pooling layer

    Parameters
    ----------
    A_prev : numpy array of shape (m, n_H_prev, n_W_prev, n_C_prev)
        Input data, m samples
    hyperparams : python dictionary
        must containing the following parameters:
        pool_filter_size : int, the size of pool filter
        pool_stride : int, the stride of pool
        mode : string ("max" or "average"), the pooling mode you would like to use

    Returns:
    ----------
    A : a numpy array of shape (m, n_H, n_W, n_C)
        output of the pool layer 
    cache : cache used in the backward pass of the pooling layer, contains the input and hyperparams
    """

    # Retrieve dimensions from the input shape
    (m, inh, inw, inc) = A_prev.shape

    # Retrieve hyperparameters from "hyperparams"
    filter_size = hyperparams["pool_filter_size"]
    stride = hyperparams["pool_stride"]
    mode = hyperparams["pool_mode"]

    # Define the dimensions of the output
    outh = int(1 + (inh - filter_size) / stride)
    outw = int(1 + (inw - filter_size) / stride)
    outc = inc

    # Initialize output matrix A
    res = np.zeros((m, outh, outw, outc))
    # loop over the training examples
    for i in range(m):
        # the current sample to be processed
        sample = A_prev[i]
        # loop on the vertical axis of the output volume
        for h in range(outh):
            # loop on the horizontal axis of the output volume
            for w in range(outw):
                # loop over the channels of the output volume
                for c in range (outc):
                    # Find the corners of the current "slice" (≈4 lines)
                    starth = h * stride
                    endh = starth + filter_size
                    startw = w * stride
                    endw = startw + filter_size
                    # Compute the pooling operation on the slice. Use an if statment to differentiate the modes. Use np.max/np.mean.
                    if mode == "max":
                        res[i, h, w, c] = np.max(sample[starth:endh, startw:endw, c])
                    elif mode == "average":
                        res[i, h, w, c] = np.mean(sample[starth:endh, startw:endw, c])

    # Store the input and hyperparams in "cache" for pool_backward()
    #cache = (A_prev, hyperparams)

    return res

def conv_backward(dZ, cache):
    """
    Implement the backward propagation for a convolution function

    Parameters
    ----------
    dZ : gradient of the cost with respect to the output of the conv layer (Z), numpy array of shape (m, outh, outw, outc)
    cache -- cache of values needed for the conv_backward(), output of conv_forward()

    Returns:
    ----------
    dA_prev : gradient of the cost with respect to the input of the conv layer (A_prev),
               numpy array of shape (m, inh, inw, inc)
    dW : gradient of the cost with respect to the weights of the conv layer (W)
          numpy array of shape (filter_size, filter_size, inc, outc)
    db : gradient of the cost with respect to the biases of the conv layer (b)
          numpy array of shape (1, 1, 1, outc)
    """

    # Retrieve information from "cache"
    (A_prev, W, b, hyperparams) = cache

    # Retrieve dimensions from A_prev's shape
    (m, inh, inw, inc) = A_prev.shape

    # Retrieve dimensions from W's shape
    (filter_size, filter_size, inc, outc) = W.shape

    # Retrieve information from "hyperparams"
    stride = hyperparams['conv_stride']
    pad = hyperparams['conv_pad']

    # Retrieve dimensions from dZ's shape
    (m, outh, outw, outc) = dZ.shape

    # Initialize dA_prev, dW, db with the correct shapes
    dA_prev = np.zeros((m, inh, inw, inc))
    dW = np.zeros((filter_size, filter_size, inc, outc))
    db = np.zeros((1, 1, 1, outc))

    # Pad A_prev and dA_prev
    A_prev_pad = zero_pad(A_prev, pad)
    dA_prev_pad = zero_pad(dA_prev, pad)

    # loop over the training examples
    for i in range(m):
        # select ith training example from A_prev_pad and dA_prev_pad
        a_prev_pad = A_prev_pad[i]
        da_prev_pad = dA_prev_pad[i]
        # loop on the vertical axis of the output volume
        for h in range(outh):
            # loop on the horizontal axis of the output volume
            for w in range(outw):
                # loop over the channels of the output volume
                for c in range (outc):
                    # Find the corners of the current "slice"
                    starth = h * stride
                    endh = starth + filter_size
                    startw = w * stride
                    endw = startw + filter_size
                    # Use the corners to define the slice from a_prev_pad
                    a_slice = a_prev_pad[starth:endh, startw:endw]
                    # Update gradients for the window and the filter's parameters using the code formulas given above
                    da_prev_pad[starth:endh, startw:endw] += W[:,:,:,c] * dZ[i, h, w, c]
                    dW[:,:,:,c] += a_slice * dZ[i, h, w, c]
                    db[:,:,:,c] += dZ[i, h, w, c]

        # Set the ith training example's dA_prev to the unpaded da_prev_pad (Hint: use X[pad:-pad, pad:-pad, :])
        dA_prev[i, :, :, :] = dA_prev_pad[i, pad:-pad, pad:-pad, :]

    # Making sure your output shape is correct
    assert(dA_prev.shape == (m, inh, inw, inc))

    return dA_prev, dW, db
