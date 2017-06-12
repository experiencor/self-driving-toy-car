#!/usr/bin/env python

# read_PWM.py
# 2015-12-08
# Public Domain

import time
import pigpio # http://abyz.co.uk/rpi/pigpio/python.html

class reader:
   """
   A class to read PWM pulses and calculate their frequency
   and duty cycle.  The frequency is how often the pulse
   happens per second.  The duty cycle is the percentage of
   pulse high time per cycle.
   """
   def __init__(self, pi, gpio, weighting=0.0):
      """
      Instantiate with the Pi and gpio of the PWM signal
      to monitor.

      Optionally a weighting may be specified.  This is a number
      between 0 and 1 and indicates how much the old reading
      affects the new reading.  It defaults to 0 which means
      the old reading has no effect.  This may be used to
      smooth the data.
      """
      self.pi = pi
      self.gpio = gpio

      if weighting < 0.0:
         weighting = 0.0
      elif weighting > 0.99:
         weighting = 0.99

      self._new = 1.0 - weighting # Weighting for new reading.
      self._old = weighting       # Weighting for old reading.

      self._high_tick = None
      self._period = None
      self._high = None

      pi.set_mode(gpio, pigpio.INPUT)

      self._cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

   def _cbf(self, gpio, level, tick):

      if level == 1:

         if self._high_tick is not None:
            t = pigpio.tickDiff(self._high_tick, tick)

            if self._period is not None:
               self._period = (self._old * self._period) + (self._new * t)
            else:
               self._period = t

         self._high_tick = tick

      elif level == 0:

         if self._high_tick is not None:
            t = pigpio.tickDiff(self._high_tick, tick)

            if self._high is not None:
               self._high = (self._old * self._high) + (self._new * t)
            else:
               self._high = t

   def frequency(self):
      """
      Returns the PWM frequency.
      """
      if self._period is not None:
         return 1000000.0 / self._period
      else:
         return 0.0

   def pulse_width(self):
      """
      Returns the PWM pulse width in microseconds.
      """
      if self._high is not None:
         return self._high
      else:
         return 0.0

   def duty_cycle(self):
      """
      Returns the PWM duty cycle percentage.
      """
      if self._high is not None:
         return 100.0 * self._high / self._period
      else:
         return 0.0

   def cancel(self):
      """
      Cancels the reader and releases resources.
      """
      self._cb.cancel()

if __name__ == "__main__":

   import time
   import pigpio
   import read_PWM

   PWM_GPIO = 4
   RUN_TIME = 60.0
   SAMPLE_TIME = 2.0

   pi = pigpio.pi()

   p = read_PWM.reader(pi, PWM_GPIO)

   start = time.time()

   while (time.time() - start) < RUN_TIME:

      time.sleep(SAMPLE_TIME)

      f = p.frequency()
      pw = p.pulse_width()
      dc = p.duty_cycle()
     
      print("f={:.1f} pw={} dc={:.2f}".format(f, int(pw+0.5), dc))

   p.cancel()

   pi.stop()

