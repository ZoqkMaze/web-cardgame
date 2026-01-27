# Witches
This is a small work in progress project.
It implements:
  - a python package for a witches-like card game
  - an api for playing the game
  - a prototype web-site to play the game in browser

Althought it might change in future, the package and the api are basicly finished. Just the web frontend needs huge improvements.

---

## witches package
First, you need to install the local package. Therefore, run `pip install -e package/`. Now, the package should be available and always up to date.
The python package is (hopfully enough) tested (currently 90% test coverage).
A small example of a cli implementation can be found at `package/tests/example.py`.

---

## witches API
The API uses `python` and `fastapi` as well as `nanoid`.
To run it in development, first install `fastapi` via `pip install "fastapi[standard]"` and `nanoid` using `pip install nanoid`. Then execute `fastapi dev server/api.py`. After that, it should be accessable on `http://127.0.0.1:8000`

---

## web frontend
The web frontend is currently in development.
To access it under `localhost:8080`, you can use the build-in python `http.server`. Simply, run `python -m http.server 8080` in the client directory.
Feel free to use any other server - but mind the browser cache.
Because the browsers localStorage is used, it is not possible to test multiple clients in the same browser. Therfore, use different browsers or incognito tabs for each user.
