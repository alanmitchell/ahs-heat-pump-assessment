"""Supplies constants and lists to the application
"""
import anvil.server

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
FUELS_DRYING_COOKING) = [
  ('Propane', 3),
  ('Electricity', 1),
  ('Natural Gas', 2)
]

# Space Heating System Types, based on Fuel
SPACE_HTG_SYS_TYPES = {
  
}

