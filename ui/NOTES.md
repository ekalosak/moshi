# Developer notes

## types/node
In `package.json` there's a package:
```json
    ...
    "@types/node": "^20.2.5",
    ...
```
It's installed to fix the error in
[this StackOverflow post](https://stackoverflow.com/questions/76098011/ts2585-and-ts2304-errors-while-compiling-typescript-file-with-axios).

## module: es6

In `tsconfig.json` the module is `es6` rather than the default `commonjs` for reasons specified in
[this blog post](https://blog.rendall.dev/posts/2019/1/14/problem-typescript-adds-objectdefinepropertyexports-esmodule-value-true/)
