"""Test the interactive connection establishment module."""
import pytest

from moshi import ice

@pytest.mark.asyncio
@pytest.mark.gcloud
@pytest.mark.metered
async def test_get_ice_config():
    cfg = await ice.get_ice_config()
    print(cfg)
    import sys; sys.exit(1)
