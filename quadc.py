#!/usr/bin/env python3
import requests
import json
import time
import os
import sys
import re
from typing import Dict, Any, Optional

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_text(text, delay=0.01, color="\033[35m"):
    for char in text:
        print(f"{color}{char}\033[0m", end='', flush=True)
        time.sleep(delay)
    print()

def show_header():
    clear_screen()

    header_art = """
  █████   █    ██  ▄▄▄         ▓█████▄  ▄████▄
▒██▓  ██▒ ██  ▓██▒▒████▄       ▒██▀ ██▌▒██▀ ▀█
▒██▒  ██░▓██  ▒██░▒██  ▀█▄     ░██   █▌▒▓█    ▄
░██  █▀ ░▓▓█  ░██░░██▄▄▄▄██    ░▓█▄   ▌▒▓▓▄ ▄██▒
░▒███▒█▄ ▒▒█████▓  ▓█   ▓██▒   ░▒████▓ ▒ ▓███▀ ░
░░ ▒▒░ ▒ ░▒▓▒ ▒ ▒  ▒▒   ▓▒█░    ▒▒▓  ▒ ░ ░▒ ▒  ░
 ░ ▒░  ░ ░░▒░ ░ ░   ▒   ▒▒ ░    ░ ▒  ▒   ░  ▒
   ░   ░  ░░░ ░ ░   ░   ▒       ░ ░  ░ ░
    ░       ░           ░  ░      ░    ░ ░
                                ░      ░
"""

    for line in header_art.split('\n'):
        if line:
            animate_text(line, 0.003)

    animate_text("discord: quantumpeakk", 0.02)
    animate_text("github: https://github.com/quantumpeakk", 0.02)
    animate_text("telegram: t.me/wessydll", 0.02)
    print()
    animate_text("SUNUCU SORGU TOOL", 0.03, "\033[31m")
    print()

def extract_guild_info(input_text: str) -> Optional[Dict[str, Any]]:
    try:
        invite_patterns = [
            r'(?:discord\.gg/|discord\.com/invite/)([a-zA-Z0-9]+)',
            r'^([a-zA-Z0-9]+)$'
        ]

        is_invite = False
        for pattern in invite_patterns:
            match = re.search(pattern, input_text)
            if match:
                input_text = match.group(1)
                is_invite = True
                break

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        if is_invite or not input_text.isdigit():
            response = requests.get(
                f'https://discord.com/api/v9/invites/{input_text}?with_counts=true&with_expiration=true',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                guild_data = data.get('guild', {})
                if guild_data:
                    guild_data['invite_code'] = input_text
                    guild_data['approximate_member_count'] = data.get('approximate_member_count', 'Bilinmiyor')
                    guild_data['approximate_presence_count'] = data.get('approximate_presence_count', 'Bilinmiyor')

                    if 'channel_count' not in guild_data:
                        channels = data.get('channels', [])
                        if channels:
                            guild_data['channel_count'] = len(channels)
                            text_channels = sum(1 for c in channels if c.get('type') == 0)
                            voice_channels = sum(1 for c in channels if c.get('type') == 2)
                            guild_data['text_channels'] = text_channels
                            guild_data['voice_channels'] = voice_channels

                    return guild_data
                else:
                    return {"error": "Sunucu bilgisi alınamadı"}
            elif response.status_code == 404:
                return {"error": "Davet kodu geçersiz"}
            else:
                return {"error": f"API hatası: {response.status_code}"}

        else:
            response = requests.get(
                f'https://discord.com/api/v9/guilds/{input_text}',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Sunucu bulunamadı"}
            elif response.status_code == 403:
                return {"error": "Sunucu gizli veya erişilemez"}
            else:
                return {"error": f"API hatası: {response.status_code}"}

    except requests.exceptions.Timeout:
        return {"error": "Bağlantı zaman aşımına uğradı"}
    except requests.exceptions.ConnectionError:
        return {"error": "Bağlantı hatası - İnternet kontrol et"}
    except Exception as e:
        return {"error": f"Hata: {str(e)}"}

def format_guild_info(data: Dict[str, Any]):
    print("\033[31m")
    print("╔" + "═" * 90 + "╗")
    print(f"║ {'SUNUCU BİLGİLERİ':^88} ║")
    print("╠" + "═" * 90 + "╣")

    if "error" in data:
        print(f"║ {'HATA':<20} : {data['error']:<67} ║")
    else:
        guild_id = data.get('id', 'Bilinmiyor')
        guild_name = data.get('name', 'Bilinmiyor')
        guild_desc = data.get('description', 'Yok')

        creation_date = 'Bilinmiyor'
        if guild_id != 'Bilinmiyor' and str(guild_id).isdigit():
            try:
                snowflake = int(guild_id)
                timestamp = ((snowflake >> 22) + 1420070400000) / 1000
                creation_date = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))
            except:
                creation_date = 'Bilinmiyor'

        print(f"║ {'Sunucu ID':<20} : {str(guild_id):<67} ║")
        print(f"║ {'Sunucu Adı':<20} : {str(guild_name):<67} ║")
        print(f"║ {'Açıklama':<20} : {str(guild_desc):<67} ║")
        print(f"║ {'Oluşturulma':<20} : {creation_date:<67} ║")

        member_count = data.get('approximate_member_count', data.get('member_count', 'Bilinmiyor'))
        if member_count != 'Bilinmiyor':
            print(f"║ {'Üye Sayısı':<20} : {str(member_count):<67} ║")

        presence = data.get('approximate_presence_count')
        if presence and presence != 'Bilinmiyor':
            print(f"║ {'Aktif Üye':<20} : {str(presence):<67} ║")

        channel_count = data.get('channel_count', data.get('channels', 'Bilinmiyor'))
        if channel_count != 'Bilinmiyor' and not isinstance(channel_count, list):
            print(f"║ {'Kanal Sayısı':<20} : {str(channel_count):<67} ║")

        text_channels = data.get('text_channels')
        if text_channels:
            print(f"║ {'Metin Kanalı':<20} : {str(text_channels):<67} ║")

        voice_channels = data.get('voice_channels')
        if voice_channels:
            print(f"║ {'Ses Kanalı':<20} : {str(voice_channels):<67} ║")

        roles = data.get('roles', [])
        if roles:
            print(f"║ {'Rol Sayısı':<20} : {len(roles):<67} ║")

        emojis = data.get('emojis', [])
        if emojis:
            print(f"║ {'Emoji Sayısı':<20} : {len(emojis):<67} ║")

        premium_tier = data.get('premium_tier', 'Bilinmiyor')
        if premium_tier != 'Bilinmiyor':
            print(f"║ {'Boost Seviyesi':<20} : {str(premium_tier):<67} ║")

        premium_count = data.get('premium_subscription_count')
        if premium_count:
            print(f"║ {'Boost Sayısı':<20} : {str(premium_count):<67} ║")

        verification_level = data.get('verification_level', 'Bilinmiyor')
        if verification_level != 'Bilinmiyor':
            level_names = {0: 'Yok', 1: 'Düşük', 2: 'Orta', 3: 'Yüksek', 4: 'Çok Yüksek'}
            level_str = level_names.get(verification_level, str(verification_level))
            print(f"║ {'Doğrulama':<20} : {level_str:<67} ║")

        nsfw_level = data.get('nsfw_level', 'Bilinmiyor')
        if nsfw_level != 'Bilinmiyor':
            nsfw_names = {0: 'Varsayılan', 1: 'Güvenli', 2: 'Sınırlı', 3: 'NSFW'}
            nsfw_str = nsfw_names.get(nsfw_level, str(nsfw_level))
            print(f"║ {'NSFW Seviye':<20} : {nsfw_str:<67} ║")

        owner_id = data.get('owner_id')
        if owner_id:
            print(f"║ {'Sahip ID':<20} : {str(owner_id):<67} ║")

        region = data.get('region', data.get('rtc_region', 'Bilinmiyor'))
        if region != 'Bilinmiyor':
            print(f"║ {'Bölge':<20} : {str(region):<67} ║")

        locale = data.get('preferred_locale', 'Bilinmiyor')
        if locale != 'Bilinmiyor':
            print(f"║ {'Dil':<20} : {str(locale):<67} ║")

        invite_code = data.get('invite_code')
        if invite_code:
            print(f"║ {'Davet Kodu':<20} : {str(invite_code):<67} ║")

        features = data.get('features', [])
        if features:
            feature_text = ', '.join([str(f) for f in features])
            print(f"║ {'Özellikler':<20} : {feature_text:<67} ║")

        icon = data.get('icon')
        if icon:
            icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{icon}.png"
            print(f"║ {'Icon URL':<20} : {icon_url:<67} ║")

        splash = data.get('splash')
        if splash:
            splash_url = f"https://cdn.discordapp.com/splashes/{guild_id}/{splash}.png"
            print(f"║ {'Splash URL':<20} : {splash_url:<67} ║")

        banner = data.get('banner')
        if banner:
            banner_url = f"https://cdn.discordapp.com/banners/{guild_id}/{banner}.png"
            print(f"║ {'Banner URL':<20} : {banner_url:<67} ║")

        if data.get('vanity_url_code'):
            print(f"║ {'Vanity URL':<20} : discord.gg/{data.get('vanity_url_code'):<58} ║")

        if data.get('rules_channel_id'):
            print(f"║ {'Kurallar Kanalı':<20} : {data.get('rules_channel_id'):<67} ║")

        if data.get('public_updates_channel_id'):
            print(f"║ {'Duyuru Kanalı':<20} : {data.get('public_updates_channel_id'):<67} ║")

        if data.get('afk_channel_id'):
            print(f"║ {'AFK Kanalı':<20} : {data.get('afk_channel_id'):<67} ║")

        if data.get('afk_timeout'):
            print(f"║ {'AFK Zaman Aşımı':<20} : {data.get('afk_timeout')} saniye{' ' * 50}║")

        if data.get('max_members'):
            print(f"║ {'Max Üye':<20} : {data.get('max_members'):<67} ║")

        if data.get('max_presences'):
            print(f"║ {'Max Aktif':<20} : {data.get('max_presences'):<67} ║")

        if data.get('max_video_channel_users'):
            print(f"║ {'Max Video':<20} : {data.get('max_video_channel_users'):<67} ║")

        if data.get('approximate_member_count'):
            print(f"║ {'Tahmini Üye':<20} : {data.get('approximate_member_count'):<67} ║")

        if data.get('approximate_presence_count'):
            print(f"║ {'Tahmini Aktif':<20} : {data.get('approximate_presence_count'):<67} ║")

    print("╚" + "═" * 90 + "╝")
    print("\033[0m")

def main():
    show_header()
    print()

    while True:
        query = input("\033[35mSunucu URL'si veya ID girin (çıkmak için 'exit'): \033[0m").strip()

        if not query:
            animate_text("Giriş yapılmadı!", 0.02, "\033[31m")
            continue

        if query.lower() == 'exit':
            animate_text("Görüşürüz!", 0.03, "\033[35m")
            sys.exit(0)

        animate_text("Sorgulanıyor...", 0.02, "\033[35m")

        result = extract_guild_info(query)
        format_guild_info(result)
        print()

if __name__ == "__main__":
    main()
