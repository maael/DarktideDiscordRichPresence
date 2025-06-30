local mod = get_mod("DarktideDiscordRichPresence")
local has_ffi, err = pcall(require, "ffi")
local has_jutil, jutil = pcall(require, "jit.util")
local has_os, os = pcall(require "os")

mod._debug_mode = mod:get("enable_debug_mode")

mod.debug = {
    dump = function(table, name, depth)
        if mod._debug_mode then
            mod:dump(table, name, depth)
        end
    end
}

mod:notify("Loaded Darktide Discord")

mod:notify("Plugin version: %s", DarktideDiscord and DarktideDiscord.VERSION)

mod:notify("FFI: %s %s, JIT: %s", has_ffi, err, has_jutil)
mod:notify("WINDOWS: %s, BUILD: %s, EXECUTE: %s", IS_WINDOWS, BUILD, "???")

mod.on_setting_changed = function(id)
    mod._debug_mode = mod:get("enable_debug_mode")

    mod:notify("Changed setting: %s %s", id, mod._debug_mode)
end

mod:hook_safe(CLASS.MissionIntroView, "on_enter", function(self)
  mod:set_state("state_mission_intro")
end)

mod:hook_safe(CLASS.InventoryWeaponsView, "on_enter", function(self)
  mod:set_state("state_viewing_inventory")
end)

mod:hook_safe(CLASS.InventoryCosmeticsView, "on_enter", function (self)
  mod:set_state("state_viewing_cosmetics")
end)

mod:hook_safe(CLASS.TalentBuilderView, "on_enter", function(self)
  mod:set_state("state_viewing_talents")
end)

mod:hook_safe(CLASS.MarksVendorView, "on_enter", function (self)
  mod:set_state("state_shopping")
end)

mod:hook_safe(CLASS.ClassSelectionView, "on_enter", function (self)
  mod:set_state("state_choosing_class")
end)

mod:hook_safe(CLASS.MissionBoardView, "on_enter", function (self)
  mod:set_state("state_viewing_missions")
end)

mod:hook(CLASS.StateGameplay, "on_enter", function(func, self, parent, params, creation_context, ...)
	func(self, parent, params, creation_context, ...)
  mod._mission_name = params.mission_name
  mod._mission_circumstance = params.mechanism_data.circumstance_name
  mod._mission_challenge = params.mechanism_data.challenge
  mod.debug.dump(params)
  if mod._mission_name == "hub_ship" then
    mod:set_state("state_morningstar")
  elseif mod._mission_name == "tg_shooting_range" then
    mod:set_state("state_meat_grinder")
  else
    mod:set_state("state_mission")
    if mod._debug_mode then
      mod:notify("Mission: [Name=%s] [Circumstance=%s] [Challenge=%s]", mod._mission_name, mod._mission_circumstance, mod._mission_challenge)
    end
  end
end)

mod.set_state = function (self, state)
  local player = Managers.player:local_player(1)
  if player then
    mod._player_name = player:name()
    local profile = player:profile()
    if profile then
      mod._player_archetype = profile.archetype and profile.archetype.name
      mod._player_level = profile.current_level
    end
  end

  mod._game_state = state
  if mod._debug_mode then
    mod:notify("%s (%s) the %s is %s", mod._player_name, mod._player_level, mod:localize(mod._player_archetype), mod:localize(mod._game_state))
  end
end