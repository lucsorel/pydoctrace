[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lucsorel/pydoctrace/main.svg)](https://results.pre-commit.ci/latest/github/lucsorel/pydoctrace/main)

`pydoctrace` uses [pre-commit hooks](https://pre-commit.com/) and [pre-commit.ci continuous integration](https://pre-commit.ci/) to enforce commit messages, code formatting and linting for quality and consistency sake.
See the [code conventions](#code-conventions) section if you would like to contribute to the project.

# pydoctrace

Generate diagrams by tracing Python code execution.

Here are the diagrams produced by 2 different implementations of the `factorial` function (*n * n-1 * n-2 * ... * 1*):

- a **sequence diagram** for the recursive implementation
- a **component diagram** for the looping implementation

<table>
<tbody>
<tr>
<td valign="bottom">

```python
from pydoctrace.doctrace import trace_to_sequence_puml

@trace_to_sequence_puml
def factorial_recursive(value: int) -> int:
    if value <= 1:
        return value

    return value * factorial_recursive(value - 1)
```

</td>
<td valign="bottom">

```python
from pydoctrace.doctrace import trace_to_component_puml

@trace_to_component_puml
def factorial_reduce_multiply(value: int) -> int:
    if value <= 1:
        return value

    def multiply(agg: int, value: int) -> int:
        return agg * value

    return reduce(multiply, range(1, value + 1), 1)
```

</td>
</tr>
<tr>
<td valign="top"><code>tests.modules.factorial.factorial_recursive.puml</code><br />
<img src="https://www.plantuml.com/plantuml/svg/xP31QYf144Nt_HM5Mz5nv3qJ90JHHNP1oD90AAThjB6dIgghWu8Vdu2OI8o8PEkkwNkuzr2ZPAYMcmX6oLAt4PyZfMwDbOa6ZD-lDwKgQmhlvD8gy1eL6nZBPehU1rv0sJlwdw9QgC8QsGxv_wFuMOp6MAqMAfdzHA8eJ4GvXRZwYObwqZto4eWPtJ9uWbh4vh9nRYQTHsYTqN_bN_nRZiK8D2oMDeGOc63Wt7KLSFKejDlxtKZrORRitLHkAdzIKRAi3ELfUEzskzqNq3y5FXkFYS55el_l8bBsU-UPsKEdS-KbXd1tfj7L8aOAJyIaQEHXleMYM6-zLAPOKL6u4R7FJNGV" /></td>
<td valign="top"><code>tests.modules.factorial.factorial_reduce_multiply.puml</code><br />
<img src="https://www.plantuml.com/plantuml/svg/dP3DQiCm48JlUeeXPyMEq_yIGkYbrqAFfPYjj34ciYIaDTIKl7lT7Dpcq9BciB3C_dp3RB9Gahvp4CwIYoxOtd4kjcGaf9RSTrSdjhtXkkkTjD4DSnEw63nxKNdN-aY9EZo4zoUojlKDgiKFVTfzbi4n4XiXtpXMAfBPKSF7V7meO3iUCYR-GGDU_ctq5PGn-tKymsg5ZIGQDGdrvBIENx6irtzJZo7JJmNirLwTOtO-Nv-2kqUbSQ5nfN6ZSQTHLMVXLaLn6cwfSQbnhN4xiXPZBPNQXY2SyCYU4mbRl0qeopZOO0w1bgNQiBTZaEeJ" /></td>
</tr>
</tbody>
</table>

The **sequence diagram** gives more details about the execution but can easily grow large, the **component diagram** is more concise and helps viewing the architecture behind the calls.

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

- use one of the provided decorators (diagram type and format) to decorate the function whose execution you want to document
- run your code (with a unit test, for instance): when the execution hits the decorated function, the execution is traced and a diagram is drawn to show how the functions are called, how the values are returned and how the errors are handled

`pydoctrace` is a pure Python tool relying on no other 3rd-party library to work.
The project uses only development libraries for testing and documentation purposes.

### Doc-tracing

This approach, which I called "**doc-tracing**" (tracing code execution for documentation purposes), is complementary of other approaches which generate documentation from static code analysis.
**Static code analysis** reads the source code to detect and document data structures (classes, dataclasses, named tuples, enumeration, etc.), functions names and signatures (parameters name and types, returned value types).

Useful as it is, static code analysis does not help much to understand how the code pieces work together; doc-tracing attempts to complement this approach by producing documentation while the code runs.
Some use cases:

- you start working on a legacy codebase: study the behavior of a particular function by temporarily tracing its executions
- you finished a user story, document its implementation by tracing the execution of some **integration tests** (*"given ... when ... then ..."*) to illustrate how right cases and errors are handled.
- generally, the sequence diagrams illustrate how the modules and functions interacts; and as such, **they help discussing architecture**
- tracing code execution can also be useful when teaching computer programming to illustrate how algorithms work


### How is the code execution traced?

When a function decorated by `pydoctrace` is called:

1. a context manager is created
2. during which a **tracing function** is passed to [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace), which is called when different events happen in the execution stack:
    - when functions are called
    - when values are returned
    - when exceptions are raised or handled
3. the sequence diagram is drawn and exported in a stream fashion (when possible) so that its memory footprint is minimal
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
poetry run pytest -v --cov=pydoctrace --cov-branch --cov-report term-missing --cov-fail-under 80
```

# Changelog

* `0.2.0`: PlantUML exporter for component diagrams, added unit tests
* `0.1.2`: added github actions for the automated tests and interaction with pre-commit.ci for the code linting
* `0.1.1`: [deleted release] added github actions for the automated tests and interaction with pre-commit.ci for the code linting
* `0.1.0`: ✨ first release, PlantUML exporter for sequence diagrams; diagram files are saved in the current working directory

# Licence

Unless stated otherwise, all works are licensed under the [MIT license](http://spdx.org/licenses/MIT.html), a copy of which is included [here](LICENSE).

# Contributions

* [Luc Sorel-Giffo](https://github.com/lucsorel)

## Pull requests

Pull-requests are welcome and will be processed on a best-effort basis.

Pull requests must follow the guidelines enforced by the `pre-commit` hooks:

- commit messages must follow the Angular conventions enforced by the `commitlint` hook
- code formatting must follow the conventions enforced by the `isort` and `yapf` hooks
- code linting should not detect code smells in your contributions, this is checked by the `ruff` hook

When requesting a feature, please consider involving yourself in the review process once it is developed.

## Code conventions

The code conventions are described and enforced by [pre-commit hooks](https://pre-commit.com/hooks.html) to maintain style and quality consistency across the code base.
The hooks are declared in the [.pre-commit-config.yaml](.pre-commit-config.yaml) file.

When you contribute, set the git hooks (pre-commit and commit-msg types) on your development environment:

```sh
poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Before committing, you can check your changes manually with:

```sh
# put all your changes in the git staging area (or add the changes manually and skip this)
git add -A

# run all hooks
poetry run pre-commit run --all-files

# run a specific hook
poetry run pre-commit run ruff --all-files
```

### Commit messages

Please, follow the [conventions of the Angular team](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#-commit-message-format) for commit messages.
When merging your pull-request, the new version of the project will be derived from the messages.

I use the [redjue.git-commit-plugin](https://marketplace.visualstudio.com/items?itemName=redjue.git-commit-plugin) codium/vsCode extension to help me write commit messages.

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
