#
# Test-cases of each task are typically split into a number of groups/test-suites/
# For example, they could be grouped in two suites. The first consists of
# base-tests, the rest are additional tests for validation. We could then check
# if e.g. a post-condition proposed by AI is accepted by the best-tests, and
# look at how it performs towards the whole suite (base + validation tests).
#
# It is also possible that the test-cases are grouped into three groups: base1,
# base2, and validation. When the variable below is enabled then we use both
# base1 and base2 as the base-tests (so, stronger ). 
# Else, only base1 will be used as the base-tests.
#
#
#  DEPRACATED! (not used anymore in the new evals)
CONFIG_USE_SECOND_TESTSUITE_AS_BASETESTS_TOO = True


RUN_SINGLE_TESTCASE_TIMEOUT = 10 # in seconds

# When "true", this will cause cases where AI pre/post-condition returns a None to be 
# interpreted as "I don't know", and will be ignored in the evaluation against expected
# return-value. E.g. this could be case when the AI has been explicitly instructred to indicate
# signal this "i don't know".
#
# When the flag is "false", then the above special case does not apply. That is, the pre/post
# conditon from AI is expected to return only a true or a false, and not any other type of
# value.
IGNORE_NONE_PREDICTION = False
