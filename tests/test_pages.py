from nicegui.testing import User

from pavzetest.identity import APP_NAME


async def test_zacetna_stran(user: User) -> None:
    await user.open("/")
    await user.should_see(APP_NAME)
