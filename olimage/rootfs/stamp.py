import functools
import logging
import os

import olimage.environment as env

logger = logging.getLogger(__name__)


def stamp(func):
    """
    Stamp rootfs creation. This should not be used outside of the rootfs command

    :param func: the wrapped function
    :return: the return value from the function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # Check if the environment keys are set
        for key in ['rootfs', 'debootstrap']:
            if key not in env.paths:
                raise Exception("The path \'{}\' not set in the global environment".format(key))

        # Generate stamp for the exact rootfs: .stamp_<function_<arch>-<suite>
        file = os.path.join(env.paths['rootfs'], '.stamp_' + func.__name__.lstrip('_') + '_' + os.path.basename(env.paths['debootstrap']))

        # Check if stamp exists
        if os.path.isfile(file):
            logger.debug("Found existing stamp: {}. Skipping".format(file))
            return

        # Run function
        ret = func(*args, **kwargs)

        # Stamp
        logger.debug("Creating stamp: {}".format(file))
        # TODO: Store hash sum for the directory. This way you can check for modifications
        open(file, 'x').close()

        return ret

    return wrapper
