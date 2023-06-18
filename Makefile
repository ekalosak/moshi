.PHONY: auth build login pypi-publish dev-setup build-install precheck deploy
# Source: https://web.mit.edu/gnu/doc/html/make_6.html

GOOGLE_CLOUD_PROJECT = moshi-002
GOOGLE_CLOUD_PYPI_URL = https://us-east1-python.pkg.dev/moshi-002/moshi-002-repo/

auth:
	gcloud auth login

auth-install: auth
	pip install twine keyring keyrings.google-artifactregistry-auth

build:
	rm -rf dist 2>/dev/null
	python -m build

build-install:
	pip install --upgrade pip && \
    pip install build

bump:
	sed -i -E 's/(^version = "[0-9]+\.[0-9]+\.)([0-9]+)"/echo "\1$((\2+1))\""/e' pyproject.toml

dev: auth-install build-install
	mkdir build 2>/dev/null || echo "build/ exists" && \
    pip install -e .[dev,test]

deploy:
	(cd app/ && gcloud -q app deploy) && \
		gcloud app browse

deploy-full: build-install build publish
	echo "✅ Deployed."

logs:
	gcloud app logs tail -s default

publish:
	python3 -m twine upload \
		 --repository-url $(GOOGLE_CLOUD_PYPI_URL) \
		 "dist/*" \
		 --verbose

precheck:
	@python3 -c 'import sys; assert sys.version_info >= (3, 10), f"Python version >= 3.10 required, found {sys.version_info}"' \
        && echo "✅ Python 3 version >= 3.10" \
        || (echo "❌ Python 3 version < 3.10"; exit 1)
	@pip --version >/dev/null 2>&1 \
        && echo "✅ Pip installed" \
        || (echo "❌ Pip not found"; exit 1)
	@test -n "$GOOGLE_SDK_ROOT" \
        && echo "✅ GOOGLE_SDK_ROOT present in env" \
        || echo "❌ GOOGLE_SDK_ROOT missing in env"