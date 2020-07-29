from pytest_notebook.nb_regression import NBRegressionFixture


def test_mongo():
    fixture = NBRegressionFixture(exec_timeout=50, diff_ignore=(
                                    '/cells/*/execution_count',
                                    '/metadata/language_info/version',
                                    '/cells/*/outputs')
                                  )

    file = "/notebooks/Antarctic Demo.ipynb"
    fixture.check(str(file))

    file = "/notebooks/Parquet.ipynb"
    fixture.check(str(file))