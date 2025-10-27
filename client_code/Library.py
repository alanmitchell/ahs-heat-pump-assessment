"""Supplies constants and lists to the application
"""

# Lists of Fuels.  The IDs match the IDs in the Heat Pump Calculator API (that fuel list
# comes from AkWarm).
FUELS_ALL = [
  ('Oil', 4),
  ('Propane', 3),
  ('Electricity', 1),
  ('Birch/Hardwood', 6),
  ('Spruce/Softwood', 7),
  ('Wood Pellets', 8),
  ('Natural Gas', 2)
]
# Clothes Drying & Cooking fuels
FUELS_DRYING_COOKING = [
  ('Propane', 3),
  ('Electricity', 1),
  ('Natural Gas', 2)
]

# Space Heating System Types, based on Fuel
SPACE_HTG_SYS_TYPES = {
  4: [('Boiler', 1), ('Furnace', 2), ('Toyostove or Similar', 3), ('Non-Electric Space Heater', 4)],
  3: [('Boiler', 1), ('Furnace', 2), ('Rinnai or Similar', 3), ('Non-Electric Space Heater', 4)],
  1: [('Boiler', 1), ('Furnace', 2), ('Baseboard or Radiant Htr', 5), ('Air-Source Heat Pump', 6), ('Ground-Source Heat Pump', 7), ('Water-Source Heat Pump', 8)],
  6: [('Wood Stove', 9), ('Wood Boiler', 1)],
  7: [('Wood Stove', 9), ('Wood Boiler', 1)],
  8: [('Pellet Stove', 9), ('Pellet Boiler', 1)],
  2: [('Boiler', 1), ('Furnace', 2), ('Rinnai or Similar', 3), ('Non-Electric Space Heater', 4)],
}

# Water Heating System Types
DHW_SYS_TYPES = [
  ('From Space Heater', 1),
  ('Tank Heater', 2),
  ('Instant Tankless', 3),
  ('Heat Pump Water Htr', 4)
]

HP_SOURCE = [
  ('Outdoor Air', 1),
  ('Water (e.g. Lake)', 2),
  ('Ground', 3)
]

HP_HEAT_DISTRIBUTION = [
  ('Air', 1),
  ('Hydronic/Water', 2)
]

DHW_AFTER_HP = [
  ('Same as Before', 9),
  ('From Space Heat Pump', 1),
  ('New Tank', 2),
  ('New Instant Tankless', 3),
  ('New Heat Pump Water Htr', 4)
]
