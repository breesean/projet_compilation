# Skeleton for the compilation course

## Global structure

The project is structured in three main folders:
- `compiler` that contains the source file of our compilation project
- `tests` that contains the different tests of our elements (more below)
- `examples` that contains test inputs for our elements

Surrounding those directories, several files are present as well:
- `Pipfile` and `Pipfile.lock` are available if you use [`pipenv`](https://pipenv.pypa.io/en/latest/), otherwise ignore them and look into the requirements
- `requirements.txt` contains the requirements of the project
- `README.md` this file, hello :)

## Installation

The project can be installed with `pip` in editable mode (this will make the tests work):
```bash
$ pip install -e . -r requirements.txt
```

It can then be launched with:
```python
$ python -m compiler examples/example1.c
```

## Code structure

The code is structured in the following files:
- `constants.py`: The different constants of the project (*i.e.* regex patterns, raw-coded values, etc.)
- `lexer.py`: The lexer that transforms raw text input into lexems
- `p4rser.py`: The parser that performs the syntaxical analysis
    > Note: The file is named this way to avoid a conflict with the base python `parser` module!
- `__main__.py`: This file holds the main script that is executed when using `python -m <module_name>`

## Testing the project

We provide two complete tests that run the whole lexing and parsing processes. They can be found in the `tests` directory under `test_lexer.py` and `test_parser.py` respectively.

You can run the whole test suite (of 2 tests) using:
```python
$ pytest
```

For now, the tests are basic but we are missing many important lexing features, you are encouraged to add them yourself!

> Note: The `@pytest.mark.parametrize`  decorator will run one test for each element of the supplied list. This way, we can run the test on multiple files using:

```python
@pytest.mark.parametrize
@pytest.mark.parametrize("arg", ["val1", "val2", "val3"])
def test_with_args(arg):
    # Your test here can use the arg variable!
    ...
```