#!/usr/bin/env python
PARTS = ['negative', 'positive', 'full']  # up and left is negative, down and right is positive
MODES = ['interceptor', 'injector', 'adder']


class Interceptor:
  def __init__(self):
    self.enabled = False
    self.edit_enabled = False
    self.interceptor = None
    self.watchdog = 2 * 1e9  # In 2 sec disable interceptor if there is no new messages

  def update(self, msg, msg_timestamp, current_timestamp):
    if msg_timestamp < current_timestamp - self.watchdog:
      self.enabled = False
      self.edit_enabled = False
      return

    self.enabled = msg.enabled
    self.edit_enabled = msg.editEnabled
    self.interceptor = msg

  def override_axis(self, signal, index, part, scale=1.0):
    if (not self.enabled
        or index >= len(self.interceptor.axes)
        or part not in PARTS):
      return signal

    signal_candidate = self.interceptor.axes[index] * scale
    if part == 'negative':
      signal_candidate = max(-signal_candidate, 0.)
    elif part == 'positive':
      signal_candidate = max(signal_candidate, 0.)

    if (len(self.interceptor.axesMode) <= index 
        or self.interceptor.axesMode[index] in ('', 'interceptor')):
      pass
    elif self.interceptor.axesMode[index] == 'injector':
      if signal_candidate == 0:
        signal_candidate = signal
    elif self.interceptor.axesMode[index] == 'adder':
      signal_candidate = signal + signal_candidate

    return signal_candidate

  def override_button(self, signal, index, boolean_type=True, scale=1.0, values=(True, False)):
    if (not self.enabled
        or index >= len(self.interceptor.buttons)):
      return signal

    if boolean_type:
      if self.interceptor.buttons[index] == 0.0:
        signal_candidate = values[1]
      else:
        signal_candidate = values[0]
    else:
      signal_candidate = self.interceptor.buttons[index] * scale

    return signal_candidate

  def override_carparams(self, CP):
    if self.edit_enabled:

      # editLongitudinalTuning, changing only values without BPs
      if len(CP.longitudinalTuning.kpV) == len(self.interceptor.editLongitudinalTuning.kpV):
        for idx, val in enumerate(self.interceptor.editLongitudinalTuning.kpV):
          CP.longitudinalTuning.kpV[idx] = val

      if len(CP.longitudinalTuning.kiV) == len(self.interceptor.editLongitudinalTuning.kiV):
        for idx, val in enumerate(self.interceptor.editLongitudinalTuning.kiV):
          CP.longitudinalTuning.kiV[idx] = val

      if len(CP.longitudinalTuning.deadzoneV) == len(self.interceptor.editLongitudinalTuning.deadzoneV):
        for idx, val in enumerate(self.interceptor.editLongitudinalTuning.deadzoneV):
          CP.longitudinalTuning.deadzoneV[idx] = val

      # editLateralTuning, changing only values without BPs
      if len(CP.lateralTuning.pid.kpV) == len(self.interceptor.editLateralTuning.pid.kpV):
        for idx, val in enumerate(self.interceptor.editLateralTuning.pid.kpV):
          CP.lateralTuning.pid.kpV[idx] = val

      if len(CP.lateralTuning.pid.kiV) == len(self.interceptor.editLateralTuning.pid.kiV):
        for idx, val in enumerate(self.interceptor.editLateralTuning.pid.kiV):
          CP.lateralTuning.pid.kiV[idx] = val
