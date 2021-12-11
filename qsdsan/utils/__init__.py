#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
QSDsan: Quantitative Sustainable Design for sanitation and resource recovery systems

This module is developed by:
    Yalin Li <zoe.yalin.li@gmail.com>

This module is under the University of Illinois/NCSA Open Source License.
Please refer to https://github.com/QSD-Group/QSDsan/blob/main/LICENSE.txt
for license details.
'''

# Used in other modules so need to be imported first
from . import units_of_measure
from .units_of_measure import *

from . import (
    cod,
    colors,
    components,
    construction,
    decorators,
    # descriptors, # currently not in use
    evaluation,
    getters,
    formatting,
    loading,
    misc,
    parsing,
    setters,
    utilities,
    )

from biosteam.utils import NotImplementedMethod

from .cod import *
from .colors import *
from .components import *
from .construction import *
from .decorators import *
# from .descriptors import *
from .evaluation import *
from .getters import *
from .formatting import *
from .loading import *
from .misc import *
from .parsing import *
from .setters import *
from .utilities import *


__all__ = (
    'NotImplementedMethod',
    *cod.__all__,
    *colors.__all__,
    *components.__all__,
    *construction.__all__,
    *decorators.__all__,
    # *descriptors.__all__,
    *evaluation.__all__,
    *getters.__all__,
    *formatting.__all__,
    *loading.__all__,
    *misc.__all__,
    *parsing.__all__,
    *setters.__all__,
    *units_of_measure.__all__,
    *utilities.__all__,
    )


# This tiered importing is because some modules in utils need to be imported
# before the the main modules (e.g., _component) since the main modules depend
# on them, while other modules in utils depend on the main modules.
def _secondary_importing():
    from . import (
        doc_examples,
        )