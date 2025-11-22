local mod = get_mod("DarktideDiscordRichPresence")
local BackendUtilities = require("scripts/foundation/managers/backend/utilities/backend_utilities")

mod._debug_mode = mod:get("enable_debug_mode")

mod.debug = {
    dump = function(table, name, depth)
        if mod._debug_mode then
            mod:dump(table, name, depth)
        end
    end
}

local binaries_path_handle = Mods.lua.io.popen("cd")
local binaries_path = binaries_path_handle:read()
binaries_path_handle:close()
local bin_path = table.concat({
	binaries_path:gsub("binaries", "mods"),
	mod:get_name(),
	"bin",
}, "\\")
mod:notify(string.format('Running "%s\\start-server.bat"', bin_path))
Mods.lua.io.popen(string.format('"%s\\start-server.bat"', bin_path)):close()

mod:notify("Loaded Darktide Discord")

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
    local state_string = string.format("%s", mod:localize(mod._game_state))
    local details_string = string.format("%s (%s) the %s", mod._player_name, mod._player_level, mod:localize(mod._player_archetype))
    mod:set_discord_state(state_string, details_string)
  end
end

mod.set_discord_state = function(self, state_string, details_string)
  mod:notify("Setting discord state")
  Managers.backend:url_request("localhost:3923/presence/set", {
    method = "POST",
    body = {
      state = tostring(state_string),
      details = tostring(details_string),
      large_image = "large",
      large_text = "Hover text!"
    }
  })
  mod:notify("Set discord state")
end

mod.on_all_mods_loaded = function()
  mod:notify("Loaded all mods...")
  mod:set_discord_state("In Mod Menu", "Testing discord plugin")
  mod:notify("Sent discord state")
end

mod.on_unload = function (exit_game)
  Managers.backend:url_request("localhost:3923/presence/clear", {
    method = "POST"
  })
end