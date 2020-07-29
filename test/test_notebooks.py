from pytest_notebook.nb_regression import NBRegressionFixture
import glob


def test_mongo():
    fixture = NBRegressionFixture(exec_timeout=50, diff_ignore=(
                                    '/cells/*/execution_count',
                                    '/metadata/language_info/version',
                                    '/cells/*/outputs')
                                  )

    for file in glob.glob("/notebooks/*.ipynb"):
        print(file)
        fixture.check(str(file))