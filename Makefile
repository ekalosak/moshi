.PHONY: auth build dev publish precheck
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
	./scripts/bump_version.sh

confirm:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

dev-install: auth-install build-install
	mkdir build 2>/dev/null || echo "build/ exists" && \
    pip install -e .[dev,test]

dev:
	ls **/*py | MOSHINOSECURITY=1 entr -rc python app/main.py --port 8080

publish: bump build
	python3 -m twine upload \
		 --repository-url $(GOOGLE_CLOUD_PYPI_URL) \
		 "dist/*" \
		 --verbose
	@echo "✅ Published."

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
