# CHANGELOG

<!-- version list -->

## v0.3.0 (2024-02-27)

### Build System

- Upgrade pytest, pytest-cov and pre-commit versions
  ([`786b292`](https://github.com/lucsorel/pydoctrace/commit/786b2921601d46e896f4f35d6e5059b550a187c9))

### Documentation

- **readme**: Add documentation about filename templates and call filtering
  ([`7e650f0`](https://github.com/lucsorel/pydoctrace/commit/7e650f0b97d6a015f485833a948507538e406fa5))

### Features

- **callfilter**: Start CallFilter and presets classes
  ([`e52575b`](https://github.com/lucsorel/pydoctrace/commit/e52575b9dad863e0f34f85938585ef779639cbd1))

- **doctrace,exporters**: Add templating for output file names, tracing decorators support options
  ([`0a65740`](https://github.com/lucsorel/pydoctrace/commit/0a657405dd3844c7fa8ae8515198565266146c52))

- **presets**: Add preset to filter out calls related to test suites
  ([`9f13507`](https://github.com/lucsorel/pydoctrace/commit/9f13507fee80355cfac0c7f70553b7d9fe112355))

- **presets**: Filter out calls being below a given depth in the call stack, start integration tests
  ([`1cea5dd`](https://github.com/lucsorel/pydoctrace/commit/1cea5dd2364e02ad504bc3dae93676b4e65d820d))


## v0.2.0 (2023-09-27)

### Bug Fixes

- Release version number, no lint deps during automated tests
  ([`191c8dc`](https://github.com/lucsorel/pydoctrace/commit/191c8dca140b0f2c9a037a56c3b64f16cc8e0db4))

- **component exporter**: Hide the name of the fake root package
  ([`4a56ed1`](https://github.com/lucsorel/pydoctrace/commit/4a56ed113690013fefb26cf5f589f0b288026102))

- **sequence**: Unescape line feed between error classname and message
  ([`6831f6b`](https://github.com/lucsorel/pydoctrace/commit/6831f6b57081f5ad1627bae0f08f27058d3b345b))

### Build System

- Update identify (and other sub-dependencies) version
  ([`7b82b30`](https://github.com/lucsorel/pydoctrace/commit/7b82b3054886bd5a86e0b198d04bbb89c5e27f67))

### Documentation

- **pyproject**: Rephrase the comment about the class parameter in the signature of a @classmethod
  ([`03372a6`](https://github.com/lucsorel/pydoctrace/commit/03372a60d0aa8b46dc10e8193eca26108807bc68))

- **readme**: Update documentation to account for component diagrams too
  ([`996dc53`](https://github.com/lucsorel/pydoctrace/commit/996dc53a4ff33321dfced107fbf1a0c282eb9214))

- **tracer**: Remove implemented comment
  ([`a5b46c0`](https://github.com/lucsorel/pydoctrace/commit/a5b46c07d05edaba4483917077e5280c8d59be55))

### Features

- **component**: Add exporter and decorator for PlantUML component diagram
  ([`b38a4a1`](https://github.com/lucsorel/pydoctrace/commit/b38a4a154f4b5d98335be2c8fc9fc95e9d046396))

- **component**: Display unhandled errors with a vertical arrow bubbling out of the traced function
  ([`b45c474`](https://github.com/lucsorel/pydoctrace/commit/b45c4747e3c91c1a75e84088f41719ef7adf4c25))

- **component**: Do not draw return arrows on recursive calls for readability sake
  ([`2edf6cb`](https://github.com/lucsorel/pydoctrace/commit/2edf6cb009e764af9ff33a4261cd8d6e44acad27))

- **component**: Simplify arrow label when there are more than 7 ranks
  ([`ac10d9a`](https://github.com/lucsorel/pydoctrace/commit/ac10d9a6ff85c0967108c1f72325ca550e30f661))

- **components**: Introduce a components diagram exporter WIP
  ([`7c6f660`](https://github.com/lucsorel/pydoctrace/commit/7c6f6603b9d193847dd53b93b2c3f2ddaf48a3d1))


## v0.1.1 (2023-07-03)

### Build System

- Upgrade pre-commit library
  ([`74c34a6`](https://github.com/lucsorel/pydoctrace/commit/74c34a666538ad09f5eaf04ead35c73a3eef809a))

### Documentation

- Improve code samples style, specify PlantUML comments
  ([`cbadda2`](https://github.com/lucsorel/pydoctrace/commit/cbadda2caaf1f6bf1ada747cbd6b7ab22bc93830))


## v0.1.0 (2023-02-07)

- Initial Release
