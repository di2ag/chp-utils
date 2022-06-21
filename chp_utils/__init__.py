""" Initialization file for a CHP Utils API clients.
"""

from copy import copy
import types

from .client import BaseClient
from .mixins.client.sri_node_normalizer import SriNodeNormalizerMixin
from .mixins.client.sri_ontology_kp import SriOntologyKpMixin
from chp_utils._version import __version__

# Aliases
COMMON_ALIASES = {}

# SRI Node Normalizer specific aliases
SRI_NODE_NORMALIZER_API_ALIASES = copy(COMMON_ALIASES)
SRI_NODE_NORMALIZER_API_ALIASES.update({
    "_get_normalized_nodes": 'get_normalized_nodes',
    "_get_curie_prefixes":  'get_curie_prefixes',
    "_get_semantic_types": 'get_semantic_types',
})

# SRI Ontology KP specific aliases
SRI_ONTOLOGY_KP_API_ALIASES = copy(COMMON_ALIASES)
SRI_ONTOLOGY_KP_API_ALIASES.update({
    "_query": 'query',
    "_get_ontology_descendants": 'get_ontology_descendants',
})

# Kwargs
COMMON_KWARGS = {}

# API specific kwargs
SRI_NODE_NORMALIZER_API_KWARGS = copy(COMMON_KWARGS)
SRI_NODE_NORMALIZER_API_KWARGS.update({
    "_default_url": 'https://nodenormalization-sri.renci.org/',
})

# API specific kwargs
SRI_ONTOLOGY_KP_API_KWARGS = copy(COMMON_KWARGS)
SRI_ONTOLOGY_KP_API_KWARGS.update({
    "_default_url": 'https://ontology-kp.apps.renci.org/',
})

# Client settings
CLIENT_SETTINGS = {
    "sri_node_normalizer": {
        "class_name": 'SriNodeNormalizerApiClient',
        "class_kwargs": SRI_NODE_NORMALIZER_API_KWARGS,
        "attr_aliases": SRI_NODE_NORMALIZER_API_ALIASES,
        "base_class": BaseClient,
        "mixins": [SriNodeNormalizerMixin]
    },
    "sri_ontology_kp": {
        "class_name": 'SriOntologyKpApiClient',
        "class_kwargs": SRI_ONTOLOGY_KP_API_KWARGS,
        "attr_aliases": SRI_ONTOLOGY_KP_API_ALIASES,
        "base_class": BaseClient,
        "mixins": [SriOntologyKpMixin]
    },
}

def copy_func(f, name=None):
    """ Returns a function with the same code, globals, defaults, closure, and name (unless provided a different name).
    """
    fn = types.FunctionType(f.__code__,
                            f.__globals__, name or f.__name__,
                            f.__defaults__,
                            f.__closure__)
    fn.__dict__.update(f.__dict__)
    return fn

def get_client(api=None, instance=True, *args, **kwargs):
    """ Function that returns the necessary API client.

    :param api: The api wrapper to be returned.
    :type api: str
    """
    if not api:
        url = kwargs.get('url', False)
        if not url:
            raise RuntimeError('No API type or url specified.')
    api = api.lower()
    if (api not in CLIENT_SETTINGS and not kwargs.get('url', False)):
        raise Exception('No api {}, currently avaliable. Available apis are: {}'.format(api, list(CLIENT_SETTINGS.keys())))

    _settings = CLIENT_SETTINGS[api]
    _class = type(_settings["class_name"], tuple([_settings["base_class"]] + _settings["mixins"]), _settings["class_kwargs"])
    # Set aliases
    for (src_attr, target_attr) in _settings["attr_aliases"].items():
        if getattr(_class, src_attr, False):
            setattr(_class, target_attr, copy_func(getattr(_class, src_attr), name=target_attr))
    _client = _class(*args, **kwargs) if instance else _class
    return _client

class SriNodeNormalizerApiClient(get_client('sri_node_normalizer', instance=False)):
    pass

class SriOntologyKpApiClient(get_client('sri_ontology_kp', instance=False)):
    pass
