from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..db.users import users_db

class SettingsService:
    async def get_main_menu(self):
        text = (
            "▸ <b>Control Panel</b>\n"
            "Manage your video encoding preferences and cloud storage options. "
            "Select a category below to fine-tune the output quality.\n\n"
            "• <b>Video:</b> Format, Codec, Preset, Watermark\n"
            "• <b>Audio:</b> Bitrate, Channels, Codec\n"
            "• <b>Extras:</b> Upload Mode, Subtitles"
        )
        buttons = [
            [InlineKeyboardButton("Video Parameters", callback_data="VideoSettings"), InlineKeyboardButton("Audio Parameters", callback_data="AudioSettings")],
            [InlineKeyboardButton("Extra Options", callback_data="ExtraSettings"), InlineKeyboardButton("Thumbnail", callback_data="ThumbSettings")],
            [InlineKeyboardButton("Close Panel", callback_data="closeMeh")]
        ]
        return text, InlineKeyboardMarkup(buttons)

    async def get_video_settings(self, u_id):
        user = await users_db.get_user(u_id)
        if not user: return "Error", None
        
        ext = user.get('extensions', 'MKV')
        codec = "H265 (HEVC)" if user.get('hevc') else "H264 (AVC)"
        res = user.get('resolution', 'Source')
        bits = "10-bit Color" if user.get('bits') else "8-bit Color"
        crf = user.get('crf', 22)
        tune = "Animation" if user.get('tune') else "Film/Standard"
        
        p_map = {'uf': 'Ultrafast', 'sf': 'Superfast', 'vf': 'Veryfast', 'f': 'Fast', 'm': 'Medium', 's': 'Slow'}
        preset = p_map.get(user.get('preset', 'sf'), 'Medium')
        watermark = "Enabled" if user.get('watermark') else "Disabled"
        
        text = (
            "▸ <b>Video Configuration</b>\n"
            "Adjust the visual quality, format, and encoding speed.\n\n"
            f"• <b>Format:</b> {ext}\n"
            f"• <b>Codec:</b> {codec}\n"
            f"• <b>Resolution:</b> {res}\n"
            f"• <b>CRF Quality:</b> {crf}\n"
            f"• <b>Speed Preset:</b> {preset}\n"
            f"• <b>Color Depth:</b> {bits}\n"
            f"• <b>Watermark:</b> {watermark}\n"
            f"• <b>Tuning:</b> {tune}"
        )
        
        buttons = [
            [InlineKeyboardButton(f"Container: {ext}", callback_data="triggerextensions"), InlineKeyboardButton(f"Codec: {codec.split()[0]}", callback_data="triggerHevc")],
            [InlineKeyboardButton(f"Resolution: {res}", callback_data="triggerResolution"), InlineKeyboardButton(f"Quality (CRF): {crf}", callback_data="triggerCRF")],
            [InlineKeyboardButton(f"Speed: {preset}", callback_data="triggerPreset"), InlineKeyboardButton(f"Watermark: {watermark.split()[0]}", callback_data="triggerWatermark")],
            [InlineKeyboardButton(f"Depth: {bits.split()[0]}", callback_data="triggerBits"), InlineKeyboardButton(f"Tune: {tune.split('/')[0]}", callback_data="triggertune")],
            [InlineKeyboardButton("Back to Menu", callback_data="OpenSettings")]
        ]
        return text, InlineKeyboardMarkup(buttons)

    async def get_audio_settings(self, u_id):
        user = await users_db.get_user(u_id)
        
        codec = user.get('audio', 'aac').upper()
        bitrate = user.get('bitrate', 'Source')
        channels = user.get('channels', 'Source')
        
        text = (
            "▸ <b>Audio Configuration</b>\n"
            "Adjust audio encoding parameters and track properties.\n\n"
            f"• <b>Audio Codec:</b> {codec}\n"
            f"• <b>Target Bitrate:</b> {bitrate if bitrate == 'Source' else bitrate + ' kbps'}\n"
            f"• <b>Audio Channels:</b> {channels if channels == 'Source' else channels + ' Ch'}"
        )
        
        buttons = [
            [InlineKeyboardButton(f"Audio Codec: {codec}", callback_data="triggerAudioCodec")],
            [InlineKeyboardButton(f"Bitrate: {bitrate}", callback_data="triggerbitrate"), InlineKeyboardButton(f"Channels: {channels}", callback_data="triggerAudioChannels")],
            [InlineKeyboardButton("Back to Menu", callback_data="OpenSettings")]
        ]
        return text, InlineKeyboardMarkup(buttons)

    async def get_extra_settings(self, u_id):
        user = await users_db.get_user(u_id)
        
        hard = "Enabled" if user.get('hardsub') else "Disabled"
        soft = "Enabled" if user.get('subtitles') else "Disabled"
        doc = "Document/File" if user.get('upload_as_doc') else "Streaming Video"
        
        text = (
            "▸ <b>Additional Options</b>\n"
            "Manage subtitle behavior and upload preferences.\n\n"
            f"• <b>Hardcode Subs:</b> {hard}\n"
            f"• <b>Softsub:</b> {soft}\n"
            f"• <b>Upload Pattern:</b> {doc}\n\n"
            f"🏷 <b>Rename:</b> <code>{user.get('rename_template', '{filename}')}</code>\n"
            f"✍️ <b>Watermark:</b> <code>{user.get('watermark_text', '@VideoEncoder')}</code>"
        )
        
        buttons = [
            [InlineKeyboardButton(f"Hardsub: {hard}", callback_data="triggerHardsub"), InlineKeyboardButton(f"Subtitles: {soft}", callback_data="triggerSubtitles")],
            [InlineKeyboardButton(f"Upload Type: {doc.split('/')[0]}", callback_data="triggerUploadMode")],
            [InlineKeyboardButton("Set Rename Template", callback_data="setRename")],
            [InlineKeyboardButton("Back to Menu", callback_data="OpenSettings")]
        ]
        return text, InlineKeyboardMarkup(buttons)

    async def toggle(self, u_id, key, options=None):
        user = await users_db.get_user(u_id)
        if not user: return
        
        current = user.get(key)
        if options:
            try:
                idx = options.index(current)
                next_val = options[(idx + 1) % len(options)]
            except ValueError:
                next_val = options[0]
            await users_db.update_user(u_id, {key: next_val})
        else:
            await users_db.update_user(u_id, {key: not current})

    async def update_crf(self, u_id):
        user = await users_db.get_user(u_id)
        if not user: return
        current = int(user.get('crf', 22))
        next_val = current + 1
        if next_val > 32: next_val = 16
        await users_db.update_user(u_id, {'crf': next_val})

    async def get_settings_summary(self, u_id):
        user = await users_db.get_user(u_id)
        if not user: return "▸ <b>Settings</b>\nStatus: ✗ Not Found"
        
        ext = user.get('extensions', 'MKV')
        res = user.get('resolution', 'Source')
        codec = "H265" if user.get('hevc') else "H264"
        crf = user.get('crf', 22)
        audio = user.get('audio', 'aac').upper()
        
        text = (
            f"▸ <b>Current Settings</b>\n"
            f"Status: ● Active\n\n"
            f"📹 <b>Video</b>\n"
            f"Format : {ext}\n"
            f"Quality: {res}\n"
            f"Codec  : {codec}\n"
            f"CRF    : {crf}\n\n"
            f"🔊 <b>Audio</b>\n"
            f"Codec  : {audio}\n"
            f"Bitrate: {user.get('bitrate', 'Source')}\n\n"
            f"📜 <b>Extra</b>\n"
            f"Hardsub: {'Yes' if user.get('hardsub') else 'No'}\n"
            f"Thumb  : {'Custom' if user.get('custom_thumbnail') else 'Auto-Generated'}"
        )
        return text

    async def get_thumb_settings(self, u_id):
        user = await users_db.get_user(u_id)
        has_thumb = "Custom set ✅" if user.get('custom_thumbnail') else "Auto-generated 🤖"
        
        text = (
            "▸ <b>Thumbnail Settings</b>\n"
            f"Current Mode: ● {has_thumb}\n\n"
            "<blockquote>"
            "Send any photo to me (outside this menu) to set it as your custom thumbnail.\n\n"
            "Custom thumbnails will be applied to both videos and documents."
            "</blockquote>"
        )
        
        buttons = [
            [InlineKeyboardButton("Delete Custom Thumb", callback_data="delThumb")],
            [InlineKeyboardButton("Back to Menu", callback_data="OpenSettings")]
        ]
        return text, InlineKeyboardMarkup(buttons)

settings_svc = SettingsService()
