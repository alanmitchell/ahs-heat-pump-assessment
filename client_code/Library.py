"""Supplies constants and lists to the application
"""

# Version information
VERSION_MODEL_INPUTS = "1.0"      # the structure of the model inputs

# Lists of Fuels.  The IDs match the IDs in the Heat Pump Calculator API (that fuel list
# comes from AkWarm).
FUELS_ALL = [
  ('None', None),
  ('Oil', "oil1"),
  ('Propane', "propane"),
  ('Electricity', "elec"),
  ('Birch/Har', "birch"),
  ('Spruce/Softwood', "spruce"),
  ('Wood Pellets', "pellets"),
  ('Natural Gas', "ng")
]
# Clothes Drying & Cooking fuels
FUELS_DRYING_COOKING = [
  ('Not Present', None),
  ('Propane', "propane"),
  ('Electricity', "elec"),
  ('Natural Gas', "ng")
]

# Space Heating System Types, based on Fuel
SPACE_HTG_SYS_TYPES = {
  None: [],
  "oil1": [('Boiler', "boiler"), ('Furnace', "furnace"), ('Toyostove or Similar', "hi-effic-space"), ('Non-Electric Space Heater', "space")],
  "propane": [('Boiler', "boiler"), ('Furnace', "furnace"), ('Rinnai or Similar', "hi-effic-space"), ('Non-Electric Space Heater', "space")],
  "elec": [('Boiler', "boiler"), ('Furnace', "furnace"), ('Baseboard or Radiant Htr', "elec-space"), ('Air-Source Heat Pump', "ashp"), ('Ground-Source Heat Pump', "gshp"), ('Water-Source Heat Pump', "wshp")],
  "birch": [('Wood Stove', "stove"), ('Wood Boiler', "boiler")],
  "spruce": [('Wood Stove', "stove"), ('Wood Boiler', "boiler")],
  "pellets": [('Pellet Stove', "stove"), ('Pellet Boiler', "boiler")],
  "ng": [('Boiler', "boiler"), ('Furnace', "furnace"), ('Rinnai or Similar', "hi-effic-space"), ('Non-Electric Space Heater', "space")],
}

# Water Heating System Types
DHW_SYS_TYPES = [
  ('Not Present', None),
  ('From Space Heater', "from-space-htr"),
  ('Tank Heater', "tank"),
  ('Instant Tankless', "tankless"),
  ('Heat Pump Water Htr', "hpwh")
]

HP_SOURCE = [
  ('Outdoor Air', "air"),
  ('Water (e.g. Lake)', "water"),
  ('Ground', "ground")
]

HP_HEAT_DISTRIBUTION = [
  ('Air', "air"),
  ('Hydronic/Water', "hydronic")
]

DHW_AFTER_HP = [
  ('Same as Before', "as-before"),
  ('From Space Heat Pump', "from-space-hp"),
  ('New Tank', "new-tank"),
  ('New Instant Tankless', "new-tankless"),
  ('New Heat Pump Water Htr', "new-hpwh")
]

UNSERVED_HP_LOAD = [
  ('Existing Primary System', 'primary'),
  ('Existing Secondary System', 'secondary'),
  ('Other', 'other')
]