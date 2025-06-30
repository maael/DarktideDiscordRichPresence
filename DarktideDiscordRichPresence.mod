return {
	run = function()
		fassert(rawget(_G, "new_mod"), "`DarktideDiscordRichPresence` encountered an error loading the Darktide Mod Framework.")

		new_mod("DarktideDiscordRichPresence", {
			mod_script       = "DarktideDiscordRichPresence/scripts/mods/DarktideDiscordRichPresence/DarktideDiscordRichPresence",
			mod_data         = "DarktideDiscordRichPresence/scripts/mods/DarktideDiscordRichPresence/DarktideDiscordRichPresence_data",
			mod_localization = "DarktideDiscordRichPresence/scripts/mods/DarktideDiscordRichPresence/DarktideDiscordRichPresence_localization",
		})
	end,
	packages = {},
}
