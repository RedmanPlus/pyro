# Pyro - a python compiler

Heavily inspired by [hermes_static](https://github.com/facebook/hermes/tree/static_h) project.

## What is it?

This is a compiler for a subset python programming language with a goal to make it more low-level.

### Why a subset?

Python allows for a syntax such as:

```python
def foo(x, y):
    return x + y
```

In the example above type hints are completely avoided. During compilation, it brings a huge overhead to the memory resources, and generally a bad practice (especially in a production setting). So in pyro compilation result this code will be invalid.

Also, even when using type hints, there's still a level of ambiguity in examples like these:

```python
array: list[str, int] = [1, 2, "3", "4", 5, 6]
curr_sum: int = 0
for elem in array:
    curr_sum += elem
```

The example above (even though too obvious) will fail in runtime, but during compilation this will be allowed python syntax and grammar. Pyro will disallow this behavior at compile time.

Also type hints akin to `Optional`, `NoReturn`, `Union` and others from `typing` package actually useful (and disallow the use of `Any`)

### Why not use LLVM for code generation

Because it is quite a huge dependency which does not have any bindings for python (primarily c++), and we don't want to write one. Ideally, we want two things:

1) Pyro should be written in python from ground up until it can compile itself
2) Pyro should have no dependencies, or at least as few dependencies as humanly possible

### Why is it so?

In an ideal world we envision Pyro as a package you download from pip, ad as a dependency in your `pyproject.toml`, make it compile itself using interpreted python, and then compile your code fast and efficient. This "Zero dependencies policy" is important for that final vision, since it should be easily compilable by any python interpreter past 3.11 without any woodoo magic.

## What it is not?

At least for the next couple of years - a production ready package. You can freely fork it for any of your small tasks you would like to speed up with native performance, but make note that:

1) Your target platform would probably not be supported (for now it's only x86_84 linux)
2) There will be a LOT of breaking changes with each release, as we approach the goal of self-compilation

So please proceed with care.

## What is the end goal?

The end goal is to make it easily work with generic pip packages, which will make it a viable production runtime choice for many projects written in python. How would you like a django web app working with the speed of Go server? Yeah, I want it too.

## Can I contribute?

Pull requests are open, so after browsing the code you can freely fork and make your changes. Any constructive feedback or collaboration will be appreciated
