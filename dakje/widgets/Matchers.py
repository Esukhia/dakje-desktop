import json
import logging
import time

import pybo

from functools import wraps

logger = logging.getLogger(__name__)

# Timed decorator
def timed(func):
    """This decorator prints the execution time for the decorated function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(
            func.__name__, round(end - start, 5)))
        return result
    return wrapper


class BaseRuleMatcher:
    def match(self, tokens, rules):
        raise NotImplementedError()


class SimpleRuleMatcher(BaseRuleMatcher):
    def match(self, tokens, rules):
        for rule in rules:

            @timed
            def f():
                # find the pattern to be updated
                matcher = pybo.CQLMatcher(rule.cql)
                slices = matcher.match([t.pyboToken for t in tokens])
                return slices

            slices = f()

            for slice in slices:
                # find index for the token to be updated
                matcher = pybo.CQLMatcher(rule.actionCql)
                pattern = tokens[slice[0]:slice[1] + 1]

                sliceInPattern = matcher.match(
                    [t.pyboToken for t in pattern])[0]
                # FIXME: get first match for now
                # FIXME: bug, dont match last one

                index = sliceInPattern[0] + slice[0]

                # update token's attrs
                actionToken = tokens[index]
                for key, val in json.loads(rule.action).items():
                    if hasattr(actionToken, key):
                        setattr(actionToken, key, val)
                tokens[index] = actionToken


import experta

from experta import KnowledgeEngine, Fact
from experta import Rule as expertaRule


class CQL(Fact):
    """Info about the traffic light."""
    pass

class CqlEngine(KnowledgeEngine):
    def __init__(self, tokens, actions):
        self.tokens = tokens
        self.actions = actions
        super().__init__()

    def get_rules(self):
        rules = []
        for cql, action in self.actions.items():
            rule = expertaRule(CQL(cql))
            rule._wrapped = action
            rules.append(rule)
        return rules

def featureCheckCall(self, data, is_fact=True):
    matcher = pybo.CQLMatcher(self.expected.value)
    tokens = data[0]
    slices = matcher.match([t.pyboToken for t in tokens])
    if len(slices) > 0:
        return True
    else:
        return False

experta.matchers.rete.check.FeatureCheck.__call__ = featureCheckCall

class expertaRuleMatcher():
    def match(self, tokens, rules):
        actions = dict()

        for rule in rules:
            def actionFunc(self):
                matcher = pybo.CQLMatcher(rule.cql)
                slices = matcher.match([t.pyboToken for t in tokens])
                newTokens = self.facts[1][0]

                for slice in slices:
                    # find index for the token to be updated
                    matcher = pybo.CQLMatcher(rule.actionCql)
                    pattern = tokens[slice[0]:slice[1] + 1]
                    sliceInPattern = matcher.match(
                        [t.pyboToken for t in pattern])[0]
                    index = sliceInPattern[0] + slice[0]

                    for k, v in json.loads(rule.action).items():
                        setattr(newTokens[index], k, v)

                self.declare(CQL(newTokens))

            actions[rule.cql] = actionFunc

        engine = CqlEngine(tokens, actions)
        engine.reset()
        # engine.declare(Light(color=choice(['green', 'red'])))
        engine.declare(CQL(tokens))
        engine.run()
