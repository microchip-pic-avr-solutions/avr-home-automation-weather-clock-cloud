# AVR Home Automation - Weather Clock Cloud Script

The [*Weather Clock*](https://www.youtube.com/watch?v=J-r-PiCiXmQ) is a "clock" that shows the forecasted weather instead of time. Based on the AVR-IoT WG Development Board, the weather clock communicates with the Google Cloud Platform to fetch the forecasted weather for a given location.

This repository contains a python script to fetch weather data from yr.no, cache the given data, and convert it to a clock hand position for said weather clock. This script is meant to be run as a [Google Cloud Function](https://cloud.google.com/functions). The weather clock is an example IoT project showcased through the home automation kit. For more information regarding this script, the weather clock or the home automation kit, please refer to the documents presented beneath

## Documents

* [Getting Started with the AVR® Home Automation Kit](http://www.microchip.com/DS50002957)
* [Home Automation - Weather Clock](http://www.microchip.com/DS50002962)

![](clock.png)