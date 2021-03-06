"""
Test the fastica algorithm.
"""

import numpy as np

import scikits.learn.fastica as fastica


def center_and_norm(x, axis=-1):
    """ Centers and norms x **in place**

        Parameters
        -----------
        x: ndarray
            Array with an axis of observations (statistical units) measured on
            random variables.
        axis: int, optionnal
            Axis along which the mean and variance are calculated.
    """
    x = np.rollaxis(x, axis)
    x -= x.mean(axis=0)
    x /= x.std(axis=0)


def test_gs():
    """
    Test gram schmidt orthonormalization
    """
    # generate a random orthogonal  matrix
    W, _, _ = np.linalg.svd(np.random.randn(10, 10))
    w = np.random.randn(10)
    fastica._gs_decorrelation(w, W, 10)
    assert (w**2).sum()<1.e-10
    w = np.random.randn(10)
    u = fastica._gs_decorrelation(w, W, 5)
    tmp = np.dot(u, W.T)
    assert((tmp[:5]**2).sum()<1.e-10)


def test_fastica(add_noise=False):
    """ Test the FastICA algorithm on very simple data.
    """
    import scipy.stats as st
    n_samples = 1000
    # Generate two sources:
    s1 = (2*np.sin(np.linspace(0, 100, n_samples))>0)-1
    #s1 = 2*(np.random.rand(n_samples)>.5) - 1
    s2 = st.t.rvs(1, size=n_samples)
    s = np.c_[s1, s2].T
    center_and_norm(s)
    s1, s2 = s

    # Mixing angle
    phi = 0.6
    mixing = np.array([[np.cos(phi),  np.sin(phi)],
                       [np.sin(phi), -np.cos(phi)]])
    m  = np.dot(mixing, s)

    if add_noise:
        m += 0.1*np.random.randn(2, 1000)

    center_and_norm(m)

    algorithm = ['parallel', 'deflation']
    non_linearity = ['logcosh', 'exp', 'cube']
    for nl in non_linearity:
        for algo in algorithm:
            k_, mixing_, s_ = fastica.fastica(
                m, fun=nl, algorithm=algo)

            # Check that the mixing model described in the docstring holds:
            np.testing.assert_almost_equal(s_, np.dot(np.dot(mixing_, k_), m))

            center_and_norm(s_)
            s1_, s2_ = s_
            # Check to see if the sources have been estimated
            # in the wrong order
            if abs(np.dot(s1_, s2)) > abs(np.dot(s1_, s1)):
                s2_, s1_ = s_
            s1_ *= np.sign(np.dot(s1_, s1))
            s2_ *= np.sign(np.dot(s2_, s2))

            # Check that we have estimated the original sources
            if add_noise==False:
                np.testing.assert_almost_equal(
                    np.dot(s1_, s1)/n_samples, 1, decimal=2)
                np.testing.assert_almost_equal(
                    np.dot(s2_, s2)/n_samples, 1, decimal=2)
            else:
                np.testing.assert_almost_equal(
                    np.dot(s1_, s1)/n_samples, 1, decimal=1)
                np.testing.assert_almost_equal(
                    np.dot(s2_, s2)/n_samples, 1, decimal=1)

    # Test FastICA class
    ica = fastica.FastICA(fun=nl, algorithm=algo)
    ica.fit(m)
    ica.get_mixing_matrix()


def test_non_square_fastica(add_noise=False):
    """ Test the FastICA algorithm on very simple data.
    """

    n_samples = 1000
    # Generate two sources:
    t  = np.linspace(0, 100, n_samples)
    s1 = np.sin(t)
    s2 = np.ceil(np.sin(np.pi*t))
    s = np.c_[s1, s2].T
    center_and_norm(s)
    s1, s2 = s

    # Mixing matrix
    mixing = np.random.randn(6, 2)
    m  = np.dot(mixing, s)

    if add_noise:
        m += 0.1*np.random.randn(6, n_samples)

    center_and_norm(m)

    k_, mixing_, s_ = fastica.fastica(m, n_comp=2)

    # Check that the mixing model described in the docstring holds:
    np.testing.assert_almost_equal(s_, np.dot(np.dot(mixing_, k_), m))

    center_and_norm(s_)
    s1_, s2_ = s_
    # Check to see if the sources have been estimated
    # in the wrong order
    if abs(np.dot(s1_, s2)) > abs(np.dot(s1_, s1)):
        s2_, s1_ = s_
    s1_ *= np.sign(np.dot(s1_, s1))
    s2_ *= np.sign(np.dot(s2_, s2))

    # Check that we have estimated the original sources
    if add_noise==False:
        np.testing.assert_almost_equal(np.dot(s1_, s1)/n_samples, 1, decimal=3)
        np.testing.assert_almost_equal(np.dot(s2_, s2)/n_samples, 1, decimal=3)


if __name__ == '__main__':
    import nose
    nose.run(argv=['', __file__])
