"""Standard figure configuration settings.

"""

def apply_conf(rc):
    """Applies standard config options to the provided rc.

    """
    rc('text', usetex=True)
    font = {'family' : 'serif',
            'serif':['Times'],
            'weight' : 'bold',
            'size'   : 11}
    rc('font', **font)
