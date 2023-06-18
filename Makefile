# Source: https://web.mit.edu/gnu/doc/html/make_6.html
.PHONY: auth build login pypi-publish dev-setup build-install

GOOGLE_CLOUD_PYPI_URL = https://us-east1-python.pkg.dev/moshi-002/moshi-002-repo/

auth:
	gcloud auth login

build:
	python -m build

build-install:
	pip install --upgrade pip && \
    pip install build

dev-setup: auth
	pip install twine keyring keyrings.google-artifactregistry-auth

pypi-publish:
	python3 -m twine upload \
		 --repository-url $(GOOGLE_CLOUD_PYPI_URL) \
		 "dist/*" \
		 --verbose
