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
CONFIG_USE_SECOND_TESTSUITE_AS_BASETESTS_TOO = True
RUN_SINGLE_TESTCASE_TIMEOUT = 10 # in seconds
