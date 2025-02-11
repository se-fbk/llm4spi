## Mutation testing

It is possible to test programs and pre/post condition checks with the mutation testing tecnique using [poodle](https://poodle.readthedocs.io/en/latest/mutation.html) tool (required for this purpose). To do so use the scripts found inside the `llm4spi/mutation` folder.
* `llm4spiJsonConverter_mutation.py`: generates python scripts containing the code that will be mutated (`<program_name>.py`) and `test_<program_name>.py`  containing the tests to be evaluated. \
	Usage: \
       `python llm4spiJsonConverter_mutation.py </path/to/json> </folder/for/mutation> <selected_test_suite> <code_to_mutate>` \
	The last two arguments are optional:
	* `<selected_test_suite>`, specifies which test suite will be used to try to kill the mutants, 
	defaults to `"validation"`, possible values: `["validation", "base0", "base1"]`
	*  `<code_to_mutate>`, specifies which part of the code will be mutated, defaults to `"PROGRAM"`, possible values: `["PROGRAM", "POST_CONDITION"]`
	
* `mutation.sh`: iterates over the folders created by `llm4spiJsonConverter_mutation.py` and uses poodle to mutate the code. Reports (both in json and html format) will be generated under the folder `./mutation-report`. \
    Usage: `. ./mutation.sh </folder/containing/subfolders/with/programs> <selected_test_suite>`
* `jsonToCsv.py`: generates a csv summary (`./output.csv`) of the results contained in the `mutation-report` folder. \ 
    Usage: `python  jsonToCsv.py </path/to/mutation-report>`