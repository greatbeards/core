"""Test ESPHome lights."""


from unittest.mock import call

from aioesphomeapi import (
    APIClient,
    APIVersion,
    LightColorCapability,
    LightInfo,
    LightState,
)
import pytest

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ATTR_MAX_COLOR_TEMP_KELVIN,
    ATTR_MAX_MIREDS,
    ATTR_MIN_COLOR_TEMP_KELVIN,
    ATTR_MIN_MIREDS,
    ATTR_RGB_COLOR,
    ATTR_RGBW_COLOR,
    ATTR_RGBWW_COLOR,
    DOMAIN as LIGHT_DOMAIN,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant


async def test_light_on_off(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic light entity that only supports on/off."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            min_mireds=153,
            max_mireds=400,
            supported_color_modes=[LightColorCapability.ON_OFF],
        )
    ]
    states = [LightState(key=1, state=True)]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [call(key=1, state=True, color_mode=LightColorCapability.ON_OFF)]
    )
    mock_client.light_command.reset_mock()


async def test_light_brightness(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic light entity that only supports brightness."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            min_mireds=153,
            max_mireds=400,
            supported_color_modes=[LightColorCapability.BRIGHTNESS],
        )
    ]
    states = [LightState(key=1, state=True, brightness=100)]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [call(key=1, state=True, color_mode=LightColorCapability.BRIGHTNESS)]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_BRIGHTNESS: 127},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.BRIGHTNESS,
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()


async def test_light_rgb(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic RGB light entity."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            supported_color_modes=[
                LightColorCapability.RGB
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS
            ],
        )
    ]
    states = [LightState(key=1, state=True, brightness=100, red=1, green=1, blue=1)]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_BRIGHTNESS: 127},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: "light.test_my_light",
            ATTR_BRIGHTNESS: 127,
            ATTR_HS_COLOR: (100, 100),
        },
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=1.0,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(pytest.approx(0.32941176470588235), 1.0, 0.0),
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_RGB_COLOR: (255, 255, 255)},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=1.0,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(1, 1, 1),
            )
        ]
    )
    mock_client.light_command.reset_mock()


async def test_light_rgbw(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic RGBW light entity."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            supported_color_modes=[
                LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS
            ],
        )
    ]
    states = [LightState(key=1, state=True, brightness=100, red=1, green=1, blue=1)]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_BRIGHTNESS: 127},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: "light.test_my_light",
            ATTR_BRIGHTNESS: 127,
            ATTR_HS_COLOR: (100, 100),
        },
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=1.0,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                white=0,
                rgb=(pytest.approx(0.32941176470588235), 1.0, 0.0),
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_RGB_COLOR: (255, 255, 255)},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=0.0,
                white=1,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(0, 0, 0),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_RGBW_COLOR: (255, 255, 255, 255)},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=1.0,
                white=1,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(1, 1, 1),
            )
        ]
    )
    mock_client.light_command.reset_mock()


async def test_light_rgbww(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic RGBWW light entity."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            min_mireds=153,
            max_mireds=400,
            supported_color_modes=[
                LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS
            ],
        )
    ]
    states = [LightState(key=1, state=True, brightness=100, red=1, green=1, blue=1)]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_BRIGHTNESS: 127},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: "light.test_my_light",
            ATTR_BRIGHTNESS: 127,
            ATTR_HS_COLOR: (100, 100),
        },
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=1.0,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                cold_white=0,
                warm_white=0,
                rgb=(pytest.approx(0.32941176470588235), 1.0, 0.0),
                brightness=pytest.approx(0.4980392156862745),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_RGB_COLOR: (255, 255, 255)},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=pytest.approx(0.4235294117647059),
                cold_white=1,
                warm_white=1,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(0, pytest.approx(0.5462962962962963), 1.0),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_RGBW_COLOR: (255, 255, 255, 255)},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=pytest.approx(0.4235294117647059),
                cold_white=1,
                warm_white=1,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(0, pytest.approx(0.5462962962962963), 1.0),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {
            ATTR_ENTITY_ID: "light.test_my_light",
            ATTR_RGBWW_COLOR: (255, 255, 255, 255, 255),
        },
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=1,
                cold_white=1,
                warm_white=1,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(1, 1, 1),
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_COLOR_TEMP_KELVIN: 2500},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_brightness=0,
                cold_white=0,
                warm_white=100,
                color_mode=LightColorCapability.RGB
                | LightColorCapability.WHITE
                | LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.COLD_WARM_WHITE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
                rgb=(0, 0, 0),
            )
        ]
    )
    mock_client.light_command.reset_mock()


async def test_light_color_temp(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic light entity that does supports color temp."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            min_mireds=153.846161,
            max_mireds=370.370361,
            supported_color_modes=[
                LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS
            ],
        )
    ]
    states = [
        LightState(
            key=1,
            state=True,
            brightness=100,
            color_temperature=153.846161,
            color_mode=LightColorCapability.COLOR_TEMPERATURE,
        )
    ]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON
    attributes = state.attributes

    assert attributes[ATTR_MIN_MIREDS] == 153
    assert attributes[ATTR_MAX_MIREDS] == 370

    assert attributes[ATTR_MIN_COLOR_TEMP_KELVIN] == 2700
    assert attributes[ATTR_MAX_COLOR_TEMP_KELVIN] == 6500
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls([call(key=1, state=False)])
    mock_client.light_command.reset_mock()


async def test_light_color_temp_no_mireds_set(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a generic color temp with no mireds set uses the defaults."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            min_mireds=0,
            max_mireds=0,
            supported_color_modes=[
                LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS
            ],
        )
    ]
    states = [
        LightState(
            key=1,
            state=True,
            brightness=100,
            color_temperature=153.846161,
            color_mode=LightColorCapability.COLOR_TEMPERATURE,
        )
    ]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON
    attributes = state.attributes

    assert attributes[ATTR_MIN_MIREDS] is None
    assert attributes[ATTR_MAX_MIREDS] is None

    assert attributes[ATTR_MIN_COLOR_TEMP_KELVIN] == 0
    assert attributes[ATTR_MAX_COLOR_TEMP_KELVIN] == 0
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light", ATTR_COLOR_TEMP_KELVIN: 6000},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_temperature=pytest.approx(166.66666666666666),
                color_mode=LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls([call(key=1, state=False)])
    mock_client.light_command.reset_mock()


async def test_light_color_temp_legacy(
    hass: HomeAssistant, mock_client: APIClient, mock_generic_device_entry
) -> None:
    """Test a legacy light entity that does supports color temp."""
    mock_client.api_version = APIVersion(1, 7)
    entity_info = [
        LightInfo(
            object_id="mylight",
            key=1,
            name="my light",
            unique_id="my_light",
            min_mireds=153.846161,
            max_mireds=370.370361,
            supported_color_modes=[
                LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS
            ],
            legacy_supports_brightness=True,
            legacy_supports_color_temperature=True,
        )
    ]
    states = [
        LightState(
            key=1,
            state=True,
            brightness=100,
            red=1,
            green=1,
            blue=1,
            white=1,
            cold_white=1,
            color_temperature=153.846161,
            color_mode=19,
        )
    ]
    user_service = []
    await mock_generic_device_entry(
        mock_client=mock_client,
        entity_info=entity_info,
        user_service=user_service,
        states=states,
    )
    state = hass.states.get("light.test_my_light")
    assert state is not None
    assert state.state == STATE_ON
    attributes = state.attributes

    assert attributes[ATTR_MIN_MIREDS] == 153
    assert attributes[ATTR_MAX_MIREDS] == 370

    assert attributes[ATTR_MIN_COLOR_TEMP_KELVIN] == 2700
    assert attributes[ATTR_MAX_COLOR_TEMP_KELVIN] == 6500
    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls(
        [
            call(
                key=1,
                state=True,
                color_mode=LightColorCapability.COLOR_TEMPERATURE
                | LightColorCapability.ON_OFF
                | LightColorCapability.BRIGHTNESS,
            )
        ]
    )
    mock_client.light_command.reset_mock()

    await hass.services.async_call(
        LIGHT_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: "light.test_my_light"},
        blocking=True,
    )
    mock_client.light_command.assert_has_calls([call(key=1, state=False)])
    mock_client.light_command.reset_mock()