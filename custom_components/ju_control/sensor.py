"""Sensor platform for ju_control."""
from homeassistant.components.sensor import SensorEntity

from homeassistant.const import VOLUME_LITERS

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import JuControlEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([JuControlSensor(coordinator, entry)])


class JuControlSensor(JuControlEntity, SensorEntity):
    """ju_control Sensor class."""

    _attr_native_unit_of_measurement = VOLUME_LITERS

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_Gesamtwasserverbrauch"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get("body")


#    @property
#    def icon(self):
#        """Return the icon of the sensor."""
#        return ICON
