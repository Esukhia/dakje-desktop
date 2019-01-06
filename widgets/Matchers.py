import json

import pybo


class BaseRuleMatcher:
    def match(self, tokens, rules):
        raise NotImplementedError()


class SimpleRuleMatcher(BaseRuleMatcher):
    def match(self, tokens, rules):
        for rule in rules:
            # find the pattern to be updated
            matcher = pybo.CQLMatcher(rule.cql)
            slices = matcher.match([t.pyboToken for t in tokens])

            for slice in slices:
                # find index for the token to be updated
                matcher = pybo.CQLMatcher(rule.actionCql)
                pattern = tokens[slice[0]:slice[1] + 2]

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


class PyKnowRuleMatcher():
    ...
