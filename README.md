# pydoctrace

Generate sequence diagrams by tracing Python code execution.

Here are the sequence diagrams produced by 2 different implementations of the `factorial` function (*n * n-1 * n-2 * ... * 1*).
One which loops, another one that is recursive:

<table>
<tbody>
<tr>
<td valign="bottom">

```python
from pydoctrace.doctrace import trace_to_puml

@trace_to_puml
def factorial_reduce_multiply(value: int) -> int:
    if value <= 1:
        return value

    def multiply(agg: int, value: int) -> int:
        return agg * value

    return reduce(multiply, range(1, value + 1), 1)
```

</td>
<td valign="bottom">

```python
from pydoctrace.doctrace import trace_to_puml

@trace_to_puml
def factorial_recursive(value: int) -> int:
    if value <= 1:
        return value

    return value * factorial_recursive(value - 1)
```

</td>
</tr>
<tr>
<td valign="top"><code>tests.modules.factorial.factorial_reduce_multiply.puml</code><br />
<img src="https://www.plantuml.com/plantuml/svg/rP0nYof148Jp_XMDgUYweZwHnqCqUDaXNEY1Z3kzEZZRlVJsW88__WAvKmurCBhDXgcYwgkUD-RKKXNHgB6cNubFaPf-wGeJ3IvUNnibdmhQL2bQgEC9caFWsgchS277bVC-y0xpmSt_ogc58jIExKiVtyXlOhHmnM6dajWl9OhYKfIR40y_RQAUz69v3yJiO1yyOIbYMpa2hANt3piFHdpmmnKTO3523RkzpJ069Xpb0AyauLE2gwtRlNH6AhyhftSmnW1AbfGnlwDEu7m-_pRGOLj09wsvwAWjfFbmq1RKFyzGrtzxFNo5T_OWTmfGYXWf_YScTKOUjoVCilhafJ1r1MKPp8bzgY9y0W00" /></td>
<td valign="top"><code>tests.modules.factorial.factorial_recursive.puml</code><br />
<img src="https://www.plantuml.com/plantuml/svg/xP31QYf144Nt_HM5Mz5nv3qJ90JHHNP1oD90AAThjB6dIgghWu8Vdu2OI8o8PEkkwNkuzr2ZPAYMcmX6oLAt4PyZfMwDbOa6ZD-lDwKgQmhlvD8gy1eL6nZBPehU1rv0sJlwdw9QgC8QsGxv_wFuMOp6MAqMAfdzHA8eJ4GvXRZwYObwqZto4eWPtJ9uWbh4vh9nRYQTHsYTqN_bN_nRZiK8D2oMDeGOc63Wt7KLSFKejDlxtKZrORRitLHkAdzIKRAi3ELfUEzskzqNq3y5FXkFYS55el_l8bBsU-UPsKEdS-KbXd1tfj7L8aOAJyIaQEHXleMYM6-zLAPOKL6u4R7FJNGV" /></td>
</tr>
</tbody>
</table>

## Installation

Use your favorite dependency manager to install `pydoctrace`:

```sh
# using pip
pip install pydoctrace

# using poetry
poetry add pydoctrace

# using pipenv
pipenv install pydoctrace
```

## Purposes and mechanisms

The purpose of `pydoctrace` is to document the execution of some code to illustrate the behavior and the structure of the code base.

- the documentation produced is a sequence diagram;
which lets you see how the functions are called, how the values are returned and how the errors are handled
- with one of the provided decorators (depending on the export format you want), decorate the function whose execution you want to document
- run your code, when the execution hits the decorated function, the execution is traced and the sequence diagram will be drawn in the format of your choice

`pydoctrace` is a pure Python tool relying on no other 3rd-party library to work.
The project involves development libraries for testing and documentation purposes.

### Doc-tracing

This approach, which I called "doc-tracing" (tracing code execution for documentation purposes), is meant to be complementary of other approaches which generate documentation from static code analysis.
Static code analysis reads the source code to detect and document data structures (classes, dataclasses, named tuples, enumeration, etc.), functions names and signatures (parameters name and types, returned value types).

Useful as it is, static code analysis does not help much to understand how the code pieces work together; doc-tracing attempts to complement this approach by producing documentation while the code runs.
Some use cases:

- you start working on a legacy codebase: study the behavior of a particular function by temporarily tracing its executions
- you finished a user story, document its implementation by tracing the execution of some **integration tests** (*"given ... when ... then ..."*) to illustrate how right cases and errors are handled.
- generally, the sequence diagrams illustrate how the modules and functions interacts; and as such, **they help discussing architecture**
- tracing code execution can also be useful when teaching computer programming to illustrate how algorithms work


### How is the code execution traced?

When a function decorated by `pydoctrace` is called:

1. a context manager is created
2. during which a **tracing function** is passed to [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace), which is called when different events happens in the execution stack:
    - when functions are called
    - when values are returned
    - when exceptions are raised or handled
3. the sequence diagram is drawn and exported in a file alongside the code execution so that its memory footprint is minimal
4. once the decorated function stops its execution, the tracing function is removed from the code execution

⚠️ **Caveat**: `pydoctrace` uses the `sys.settrace` API, which is meant to be used by debuggers.
Therefore, a warning is emitted when `pydoctrace` is used in a debug mode (and does not trace the decorated function anymore).

# Tests

```sh
# directly with poetry
poetry run pytest -v

# in an activated virtual environment
pytest -v
```

Code coverage (with [missed branch statements](https://pytest-cov.readthedocs.io/en/latest/config.html?highlight=--cov-branch)):

```sh
poetry run pytest -v --cov=pydoctrace --cov-branch --cov-report term-missing --cov-fail-under 50
```

# Changelog

* `0.1.0`: ✨ first release, PlantUML exporter; diagram files are saved in the current working directory

# Licence

Unless stated otherwise all works are licensed under the [MIT license](http://spdx.org/licenses/MIT.html), a copy of which is included [here](LICENSE).

# Contributions

* [Luc Sorel-Giffo](https://github.com/lucsorel)

## Pull requests

Pull-requests are welcome and will be processed on a best-effort basis.

Pull requests must follow the guidelines enforced by the `pre-commit` hooks:

- commit messages must follow the Angular conventions enforced by the `commitlint` hook
- code formatting must follow the conventions enforced by the `isort` and `yapf` hooks
- code linting should not detect code smells in your contributions, this is checked by the `ruff` hook

## Code conventions

The code conventions are described and enforced by [pre-commit hooks](https://pre-commit.com/hooks.html) to maintain consistency across the code base.
The hooks are declared in the [.pre-commit-config.yaml](.pre-commit-config.yaml) file.

Set the git hooks (pre-commit and commit-msg types):

```sh
poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Before committing, you can check your changes with:

```sh
# put all your changes in the git staging area
git add -A

# all hooks
poetry run pre-commit run --all-files

# a specific hook
poetry run pre-commit run ruff --all-files
```

### Commit messages

Please, follow the [conventions of the Angular team](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format) for commit messages.
When merging your pull-request, the new version of the project will be derived from the messages.

### Code formatting

This project uses `isort` and `yapf` to format the code.
The guidelines are expressed in their respective sections in the [pyproject.toml](pyproject.toml) file.

### Best practices

This project uses the `ruff` linter, which is configured in its section in the [pyproject.toml](pyproject.toml) file.

# Similar tools and bibliography

- https://stackoverflow.com/questions/45238329/it-is-possible-to-generate-sequence-diagram-from-python-code
- https://github.com/gaogaotiantian/viztracer
- https://9to5answer.com/how-to-generate-a-sequence-diagram-from-java-source-code
- https://medium.com/javarevisited/how-to-generate-sequence-diagrams-in-intellij-e2bb7cec2b0b
