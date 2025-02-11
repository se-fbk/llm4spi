## Test Generation

It is possible to generate test for programs used for pre/post condition checks generation using the [pynguin](https://www.pynguin.eu/) framework (required for this purpose).
To do so use the scripts found inside the `llm4spi/testgen` folder.
* `llm4spiJsonConverter_testgen.py`: generates python scripts containing the program for which tests will be generated. \
	Usage: \
      `python llm4spiJsonConverter_testgen.py </path/to/json> </folder/for/test/generation>`
	
* `testgen.sh`: iterates over the folders created by `llm4spiJsonConverter_testgen.py` and uses pynguin to generate the tests. The generated tests will be contained in `test_<program_name>.py`, additionally the folder `pynguin_results` will be created containing a report of the test generation process. To use the pynguin framework the environment variable `PYNGUIN_DANGER_AWARE` should be set to anything (`EXPORT PYNGUIN_DANGER_AWARE=yes`). \
 Usage: `. ./testgen.sh </folder/containing/subfolders/with/programs>`