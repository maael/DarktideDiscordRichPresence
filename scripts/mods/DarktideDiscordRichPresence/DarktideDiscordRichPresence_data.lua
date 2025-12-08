local mod = get_mod("DarktideDiscordRichPresence")

return {
	name = mod:localize("mod_name"),
	description = mod:localize("mod_description"),
	is_togglable = true,
	options = {
		widgets = {
			{
				setting_id = "enable_debug_mode",
				type = "checkbox",
				default_value = false,
			},
			{
				setting_id = "toggle_server",
				type = "checkbox",
				default_value = false,
			},
		}
	}
}
