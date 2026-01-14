# Witches
This is a small work in progress project.
It implements:
  - a python package for a witches-like card game
  - an api for playing the game
  - a prototype web-site to play the game in browser

Althought it might change in future, the package and the api are basicly finished. Just the web frontend needs huge improvements.

---

## witches package
The python package is (hopfully enough) tested (currently 90% test coverage).
A small example of a cli implementation can be found at `package/tests/example.py`.

---

## witches API
The API uses `python` and `fastapi`.
To run it in development, first install `fastapi` via `pip install "fastapi[standard]"` and then execute `fastapi dev server/api.py`. After that, it should be accessable on `http://127.0.0.1:8000`

---

## web frontend
The web frontend is currently in development.
