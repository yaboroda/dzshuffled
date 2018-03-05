# tests for dzshuffled


#### current test coverage state
```
Name                          Stmts   Miss  Cover
-------------------------------------------------
dztoolset/__init__.py             0      0   100%
dztoolset/config.py              55      3    95%
dztoolset/deezerapi.py           57      6    89%
dztoolset/deezerauth.py          78     78     0%
dztoolset/deezerconfig.py         6      6     0%
dztoolset/deezerplaylist.py      70     70     0%
dztoolset/deezerscenario.py      49     49     0%
dztoolset/deezertool.py          60     60     0%
dztoolset/printer.py             11      2    82%
-------------------------------------------------
TOTAL                           386    274    29%
```

#### requirements
 - python3
 - python module [requests](http://docs.python-requests.org/en/master/user/install/)
 - python module [pytest](https://docs.pytest.org/en/latest/getting-started.html)
 - python module [pytest-mock](https://pypi.python.org/pypi/pytest-mock)
 - for building coverage report python module [pytest-cov](https://pypi.python.org/pypi/pytest-cov)

#### run tests  
```sh
python -m pytest tests/
```