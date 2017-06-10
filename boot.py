# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import gc
import webrepl

esp.osdebug(None)
# esp.sleep_type(esp.SLEEP_LIGHT)

webrepl.start()
gc.collect()
